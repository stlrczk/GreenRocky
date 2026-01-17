from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TenderMetadata(BaseModel):
    """Metadata for a tender."""
    name: str
    organization: str
    submission_deadline: str
    initiation_date: str
    procedure_type: Optional[str] = None
    source_type: str


class Tender(BaseModel):
    """Tender model matching the JSON structure."""
    tender_url: str
    metadata: TenderMetadata
    files_count: int
    file_urls: List[str]

    @property
    def id(self) -> str:
        """Extract tender ID from URL."""
        # Extract ID from URL like https://platformazakupowa.pl/transakcja/1243607
        return self.tender_url.split('/')[-1]


class RankedTender(BaseModel):
    """Tender with ranking information."""
    id: str
    tender_url: str
    name: str
    organization: str
    submission_deadline: str
    initiation_date: str
    procedure_type: Optional[str] = None
    source_type: str
    files_count: int
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    ranking_position: int = Field(..., ge=1)
    user_feedback: Optional[str] = None  # "positive" or "negative"


class TendersResponse(BaseModel):
    """Response model for GET /api/tenders."""
    count: int
    target_date: str
    tenders: List[dict]


class TendersList(BaseModel):
    """Root structure of Tenders_List.json."""
    target_date: str
    count: int
    tenders: List[Tender]
