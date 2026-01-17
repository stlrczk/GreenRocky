import numpy as np
from typing import Dict, List, Tuple
from app.models.tender import RankedTender


class RankingService:
    """Service for ranking tenders based on similarity and feedback."""

    def calculate_cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec_a: First vector
            vec_b: Second vector

        Returns:
            Similarity score between 0 and 1
        """
        a = np.array(vec_a)
        b = np.array(vec_b)

        # Calculate cosine similarity
        similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Convert from [-1, 1] to [0, 1] range
        return float((similarity + 1) / 2)

    def rank_tenders(
        self,
        company_embedding: List[float],
        tender_embeddings: Dict[str, List[float]],
        tenders_data: list,
        top_n: int = 100
    ) -> List[Tuple[str, float]]:
        """
        Rank tenders by similarity to company description.

        Args:
            company_embedding: Embedding vector for company description
            tender_embeddings: Dictionary mapping tender_id to embedding
            tenders_data: List of Tender objects
            top_n: Number of top results to return

        Returns:
            List of (tender_id, similarity_score) tuples, sorted by score
        """
        similarities = []

        for tender in tenders_data:
            tender_id = tender.id
            if tender_id in tender_embeddings:
                tender_embedding = tender_embeddings[tender_id]
                similarity = self.calculate_cosine_similarity(company_embedding, tender_embedding)
                similarities.append((tender_id, similarity))

        # Sort by similarity score descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top N
        return similarities[:top_n]

    def apply_feedback_weights(
        self,
        ranked_tenders: List[Tuple[str, float]],
        feedback_weights: Dict[str, float]
    ) -> List[Tuple[str, float]]:
        """
        Apply feedback weights to similarity scores and re-rank.

        Args:
            ranked_tenders: List of (tender_id, similarity_score) tuples
            feedback_weights: Dictionary mapping tender_id to feedback weight

        Returns:
            Re-ranked list of (tender_id, adjusted_score) tuples
        """
        adjusted_tenders = []

        for tender_id, similarity_score in ranked_tenders:
            # Get feedback weight for this tender (default 0 if no feedback)
            weight = feedback_weights.get(tender_id, 0.0)

            # Calculate final score: similarity * (1 + weight)
            final_score = similarity_score * (1 + weight)

            adjusted_tenders.append((tender_id, final_score))

        # Re-sort by adjusted score
        adjusted_tenders.sort(key=lambda x: x[1], reverse=True)

        return adjusted_tenders

    def create_ranked_tender_response(
        self,
        ranked_results: List[Tuple[str, float]],
        tenders_dict: Dict[str, any],
        feedback_data: Dict[str, dict] = None
    ) -> List[RankedTender]:
        """
        Create RankedTender objects from ranking results.

        Args:
            ranked_results: List of (tender_id, score) tuples
            tenders_dict: Dictionary mapping tender_id to Tender object
            feedback_data: Dictionary mapping tender_id to feedback info

        Returns:
            List of RankedTender objects
        """
        ranked_tenders = []

        for position, (tender_id, score) in enumerate(ranked_results, start=1):
            tender = tenders_dict.get(tender_id)
            if not tender:
                continue

            # Determine user feedback status
            user_feedback = None
            if feedback_data and tender_id in feedback_data:
                feedback_info = feedback_data[tender_id]
                if feedback_info['positive'] > feedback_info['negative']:
                    user_feedback = "positive"
                elif feedback_info['negative'] > feedback_info['positive']:
                    user_feedback = "negative"

            ranked_tender = RankedTender(
                id=tender_id,
                tender_url=tender.tender_url,
                name=tender.metadata.name,
                organization=tender.metadata.organization,
                submission_deadline=tender.metadata.submission_deadline,
                initiation_date=tender.metadata.initiation_date,
                procedure_type=tender.metadata.procedure_type,
                source_type=tender.metadata.source_type,
                files_count=tender.files_count,
                relevance_score=round(score, 4),
                ranking_position=position,
                user_feedback=user_feedback
            )

            ranked_tenders.append(ranked_tender)

        return ranked_tenders
