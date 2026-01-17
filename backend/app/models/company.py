from pydantic import BaseModel, Field
from typing import Optional


class CompanyProfileRequest(BaseModel):
    """Request model for ranking tenders based on company profile."""
    company_description: str = Field(..., min_length=10, max_length=10000)
    top_n: int = Field(default=100, ge=1, le=1500)
    use_feedback: bool = Field(default=True)


class RankingResponse(BaseModel):
    """Response model for POST /api/rank."""
    ranked_tenders: list
    total_tenders: int
    processing_time_ms: Optional[float] = None
