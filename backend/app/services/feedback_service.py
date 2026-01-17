import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from app.models.feedback import FeedbackEntry
from app.config import settings


class FeedbackService:
    """Service for managing user feedback in JSONL format."""

    def __init__(self, feedback_file: str):
        self.feedback_file = Path(feedback_file)
        self._cache = None
        self._cache_timestamp = None
        self.cache_ttl = 300  # 5 minutes in seconds

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

    def calculate_feedback_weights(self) -> Dict[str, float]:
        """
        Calculate feedback weights for each tender.

        Weight formula: (positive - negative) / (positive + negative + smoothing_factor)

        Returns:
            Dictionary mapping tender_id to feedback weight
        """
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
