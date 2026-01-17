import json
from typing import Dict, List, Set
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import numpy as np
from app.models.feedback import FeedbackEntry
from app.config import settings


class FeedbackService:
    """Service for managing user feedback in JSONL format."""

    def __init__(self, feedback_file: str):
        self.feedback_file = Path(feedback_file)
        self._cache = None
        self._cache_timestamp = None
        self.cache_ttl = 300  # 5 minutes in seconds
        self._company_embeddings_cache = {}

    def add_feedback(
        self,
        tender_id: str,
        company_hash: str,
        feedback: str,
        session_id: str = ""
    ):
        """
        Add a feedback entry to the JSONL file.

        Args:
            tender_id: The tender ID
            company_hash: Hash of the company description
            feedback: "positive" or "negative"
            session_id: Optional session identifier
        """
        # Ensure directory exists
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)

        # Create feedback entry
        entry = FeedbackEntry(
            tender_id=tender_id,
            company_hash=company_hash,
            feedback=feedback,
            timestamp=datetime.utcnow().isoformat() + "Z",
            session_id=session_id
        )

        # Append to JSONL file
        with open(self.feedback_file, 'a', encoding='utf-8') as f:
            f.write(entry.model_dump_json() + '\n')

        # Invalidate cache
        self._cache = None

    def load_feedback(self) -> List[FeedbackEntry]:
        """
        Load all feedback from JSONL file.

        Returns:
            List of FeedbackEntry objects
        """
        # Check if file exists
        if not self.feedback_file.exists():
            return []

        # Check cache
        current_time = datetime.utcnow().timestamp()
        if self._cache is not None and self._cache_timestamp is not None:
            if current_time - self._cache_timestamp < self.cache_ttl:
                return self._cache

        # Load from file
        feedback_entries = []
        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        entry = FeedbackEntry(**data)
                        feedback_entries.append(entry)
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Warning: Skipping invalid feedback entry: {e}")
                        continue

        # Update cache
        self._cache = feedback_entries
        self._cache_timestamp = current_time

        return feedback_entries

    def get_all_feedback_by_tender(self) -> Dict[str, dict]:
        """
        Get feedback grouped by tender ID.

        Returns:
            Dictionary mapping tender_id to feedback counts
            Format: {tender_id: {"positive": count, "negative": count}}
        """
        feedback_entries = self.load_feedback()
        feedback_by_tender = defaultdict(lambda: {"positive": 0, "negative": 0})

        for entry in feedback_entries:
            if entry.feedback == "positive":
                feedback_by_tender[entry.tender_id]["positive"] += 1
            elif entry.feedback == "negative":
                feedback_by_tender[entry.tender_id]["negative"] += 1

        return dict(feedback_by_tender)

    def save_company_embedding(self, company_hash: str, embedding: List[float]):
        """
        Save company embedding to JSONL file.

        Args:
            company_hash: SHA-256 hash of company description
            embedding: 1536-dimensional embedding vector
        """
        # Load existing embeddings
        existing = self.load_company_embeddings()

        # Check if already exists
        if company_hash in existing:
            return  # Already saved

        # Ensure directory exists
        company_embeddings_file = Path(settings.company_embeddings_file)
        company_embeddings_file.parent.mkdir(parents=True, exist_ok=True)

        # Append new embedding
        entry = {
            "company_hash": company_hash,
            "embedding": embedding,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        with open(company_embeddings_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

        # Update cache
        self._company_embeddings_cache[company_hash] = embedding

    def load_company_embeddings(self) -> Dict[str, List[float]]:
        """
        Load all company embeddings from JSONL file.

        Returns:
            Dictionary mapping company_hash to embedding vector
        """
        if self._company_embeddings_cache:
            return self._company_embeddings_cache

        embeddings = {}
        file_path = Path(settings.company_embeddings_file)

        if not file_path.exists():
            return {}

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        embeddings[data["company_hash"]] = data["embedding"]
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Warning: Skipping invalid company embedding: {e}")
                        continue

        self._company_embeddings_cache = embeddings
        return embeddings

    def calculate_company_similarity(
        self,
        company_embedding: List[float],
        other_embedding: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two company embeddings.

        Args:
            company_embedding: First embedding vector
            other_embedding: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        a = np.array(company_embedding)
        b = np.array(other_embedding)

        similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return float((similarity + 1) / 2)  # Normalize to [0, 1]

    def get_similar_companies(
        self,
        company_embedding: List[float],
        threshold: float = 0.7
    ) -> Set[str]:
        """
        Get company_hashes of companies similar to the given embedding.

        Args:
            company_embedding: Embedding vector to compare against
            threshold: Minimum similarity score (0-1)

        Returns:
            Set of company_hashes with similarity >= threshold
        """
        company_embeddings = self.load_company_embeddings()
        similar_companies = set()

        for company_hash, other_embedding in company_embeddings.items():
            similarity = self.calculate_company_similarity(company_embedding, other_embedding)
            if similarity >= threshold:
                similar_companies.add(company_hash)

        return similar_companies

    def get_feedback_for_similar_companies(
        self,
        company_embedding: List[float],
        similarity_threshold: float = 0.7
    ) -> Dict[str, dict]:
        """
        Get feedback aggregated only from companies similar to the given one.

        Args:
            company_embedding: Embedding vector of current company
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            Dictionary mapping tender_id to feedback counts
            Format: {tender_id: {"positive": count, "negative": count}}
        """
        # Get all company hashes that are similar
        similar_companies = self.get_similar_companies(company_embedding, similarity_threshold)

        # Load all feedback
        feedback_entries = self.load_feedback()

        # Aggregate feedback only from similar companies
        feedback_by_tender = defaultdict(lambda: {"positive": 0, "negative": 0})

        for entry in feedback_entries:
            # Only count if feedback came from a similar company
            if entry.company_hash in similar_companies:
                if entry.feedback == "positive":
                    feedback_by_tender[entry.tender_id]["positive"] += 1
                else:
                    feedback_by_tender[entry.tender_id]["negative"] += 1

        return dict(feedback_by_tender)

    def calculate_feedback_weights(
        self,
        company_embedding: List[float] = None,
        similarity_threshold: float = 0.7
    ) -> Dict[str, float]:
        """
        Calculate feedback weights for each tender.

        If company_embedding provided: Use only feedback from similar companies
        If company_embedding is None: Use global feedback (backward compatible)

        Weight formula: (positive - negative) / (positive + negative + smoothing_factor)

        Args:
            company_embedding: Optional embedding vector for company-aware filtering
            similarity_threshold: Minimum similarity score for company filtering (0-1)

        Returns:
            Dictionary mapping tender_id to feedback weight
        """
        # Choose feedback source based on whether company_embedding is provided
        if company_embedding is not None:
            # NEW: Company-aware feedback (only from similar companies)
            feedback_by_tender = self.get_feedback_for_similar_companies(
                company_embedding,
                similarity_threshold
            )
        else:
            # OLD: Global feedback (all companies)
            feedback_by_tender = self.get_all_feedback_by_tender()

        weights = {}
        smoothing_factor = settings.feedback_smoothing_factor

        for tender_id, counts in feedback_by_tender.items():
            positive = counts["positive"]
            negative = counts["negative"]
            total = positive + negative

            if total == 0:
                weight = 0.0
            else:
                # Calculate weight with smoothing
                weight = (positive - negative) / (positive + negative + smoothing_factor)

            weights[tender_id] = weight

        return weights

    def get_feedback_stats(self) -> Dict:
        """
        Get overall feedback statistics.

        Returns:
            Dictionary with feedback statistics
        """
        feedback_entries = self.load_feedback()

        total = len(feedback_entries)
        positive = sum(1 for e in feedback_entries if e.feedback == "positive")
        negative = sum(1 for e in feedback_entries if e.feedback == "negative")

        return {
            "total_feedback_count": total,
            "positive_count": positive,
            "negative_count": negative,
            "positive_rate": round(positive / total, 3) if total > 0 else 0
        }
