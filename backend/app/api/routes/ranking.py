from fastapi import APIRouter, HTTPException
import time
import hashlib
from app.models.company import CompanyProfileRequest, RankingResponse
from app.services.tender_service import TenderService
from app.services.embedding_service import EmbeddingService
from app.services.ranking_service import RankingService
from app.services.feedback_service import FeedbackService
from app.config import settings

router = APIRouter()

# Initialize services
tender_service = TenderService(settings.tenders_file)
embedding_service = EmbeddingService(settings.embeddings_cache_file)
ranking_service = RankingService()
feedback_service = FeedbackService(settings.feedback_file)


@router.post("/rank")
async def rank_tenders(request: CompanyProfileRequest):
    """
    Rank tenders based on company description using AI embeddings.

    Args:
        request: CompanyProfileRequest containing company description and preferences

    Returns:
        RankingResponse with ranked tenders and metadata
    """
    try:
        start_time = time.time()

        # Load all tenders
        tenders = tender_service.get_all_tenders()

        # Get or generate tender embeddings (cached)
        tender_embeddings = embedding_service.get_or_generate_tender_embeddings(tenders)

        # Generate embedding for company description
        print(f"Generating embedding for company description...")
        company_embedding = embedding_service.generate_embedding(request.company_description)

        # Store company embedding immediately (for later feedback usage)
        company_hash = hashlib.sha256(request.company_description.encode('utf-8')).hexdigest()
        feedback_service.save_company_embedding(
            company_hash=company_hash,
            embedding=company_embedding
        )
        print(f"Stored company embedding with hash: {company_hash[:16]}...")

        # Rank tenders by similarity
        print(f"Ranking {len(tenders)} tenders...")
        ranked_results = ranking_service.rank_tenders(
            company_embedding=company_embedding,
            tender_embeddings=tender_embeddings,
            tenders_data=tenders,
            top_n=request.top_n
        )

        # Apply company-aware feedback weights if requested
        if request.use_feedback:
            feedback_weights = feedback_service.calculate_feedback_weights(
                company_embedding=company_embedding,
                similarity_threshold=settings.feedback_similarity_threshold
            )
            if feedback_weights:
                print(f"Applying company-aware feedback weights from {len(feedback_weights)} tenders")
                ranked_results = ranking_service.apply_feedback_weights(
                    ranked_results,
                    feedback_weights
                )

        # Create tender lookup dictionary
        tenders_dict = {tender.id: tender for tender in tenders}

        # Create response objects (without feedback data)
        ranked_tenders = ranking_service.create_ranked_tender_response(
            ranked_results,
            tenders_dict
        )

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        return {
            "ranked_tenders": [tender.model_dump() for tender in ranked_tenders],
            "total_tenders": len(tenders),
            "processing_time_ms": round(processing_time, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ranking tenders: {str(e)}")
