from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    tender_id: str
    company_description_hash: str
    feedback: Literal["positive", "negative"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    status: str
    message: str


class FeedbackEntry(BaseModel):
    """Internal model for a feedback entry in JSONL."""
    tender_id: str
    company_hash: str
    feedback: Literal["positive", "negative"]
    timestamp: str
    session_id: str = ""
