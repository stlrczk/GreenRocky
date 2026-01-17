from fastapi import APIRouter, HTTPException
from app.models.feedback import FeedbackRequest, FeedbackResponse
from app.services.feedback_service import FeedbackService
from app.config import settings

router = APIRouter()

# Initialize feedback service
feedback_service = FeedbackService(settings.feedback_file)


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit user feedback (thumbs up/down) for a tender.

    Args:
        request: FeedbackRequest containing tender_id, company_hash, and feedback

    Returns:
        FeedbackResponse with status message
    """
    try:
        # Add feedback to JSONL file
        feedback_service.add_feedback(
            tender_id=request.tender_id,
            company_hash=request.company_description_hash,
            feedback=request.feedback,
            session_id=""  # Could be enhanced with actual session tracking
        )

        return FeedbackResponse(
            status="success",
            message=f"Feedback '{request.feedback}' recorded for tender {request.tender_id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")


@router.get("/feedback/stats")
async def get_feedback_stats():
    """
    Get overall feedback statistics.

    Returns:
        Statistics about all collected feedback
    """
    try:
        stats = feedback_service.get_feedback_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feedback stats: {str(e)}")
