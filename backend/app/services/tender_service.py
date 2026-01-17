import json
from typing import Dict, List, Optional
from pathlib import Path
from app.models.tender import Tender, TendersList


class TenderService:
    """Service for loading and managing tenders."""

    def __init__(self, tenders_file: str):
        self.tenders_file = Path(tenders_file)
        self._tenders_data: Optional[TendersList] = None
        self._tenders_by_id: Dict[str, Tender] = {}

    def load_tenders(self) -> TendersList:
        """Load tenders from JSON file into memory."""
        if self._tenders_data is not None:
            return self._tenders_data

        with open(self.tenders_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self._tenders_data = TendersList(**data)

        # Build ID lookup dictionary
        for tender in self._tenders_data.tenders:
            self._tenders_by_id[tender.id] = tender

        return self._tenders_data

    def get_all_tenders(self) -> List[Tender]:
        """Get all tenders."""
        if self._tenders_data is None:
            self.load_tenders()
        return self._tenders_data.tenders

    def get_tender_by_id(self, tender_id: str) -> Optional[Tender]:
        """Get a specific tender by ID."""
        if not self._tenders_by_id:
            self.load_tenders()
        return self._tenders_by_id.get(tender_id)

    def get_tenders_count(self) -> int:
        """Get total number of tenders."""
        if self._tenders_data is None:
            self.load_tenders()
        return self._tenders_data.count

    def get_target_date(self) -> str:
        """Get the target date from tenders list."""
        if self._tenders_data is None:
            self.load_tenders()
        return self._tenders_data.target_date
