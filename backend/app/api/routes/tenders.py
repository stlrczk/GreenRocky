from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.services.tender_service import TenderService
from app.config import settings

router = APIRouter()

# Initialize tender service
tender_service = TenderService(settings.tenders_file)


@router.get("/tenders")
async def get_all_tenders():
    """
    Get all tenders from the list.

    Returns:
        - count: Total number of tenders
        - target_date: Date when the tender list was generated
        - tenders: List of all tenders with metadata
    """
    try:
        tenders_data = tender_service.get_all_tenders()

        # Convert Tender objects to simplified dict format
        tenders_list = []
        for tender in tenders_data:
            tenders_list.append({
                "id": tender.id,
                "tender_url": tender.tender_url,
                "name": tender.metadata.name,
                "organization": tender.metadata.organization,
                "submission_deadline": tender.metadata.submission_deadline,
                "initiation_date": tender.metadata.initiation_date,
                "procedure_type": tender.metadata.procedure_type,
                "source_type": tender.metadata.source_type,
                "files_count": tender.files_count
            })

        return {
            "count": tender_service.get_tenders_count(),
            "target_date": tender_service.get_target_date(),
            "tenders": tenders_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading tenders: {str(e)}")


@router.get("/tenders/{tender_id}")
async def get_tender_by_id(tender_id: str):
    """
    Get a specific tender by ID.

    Args:
        tender_id: The tender ID to retrieve

    Returns:
        Tender details including file URLs
    """
    tender = tender_service.get_tender_by_id(tender_id)

    if not tender:
        raise HTTPException(status_code=404, detail=f"Tender {tender_id} not found")

    return {
        "id": tender.id,
        "tender_url": tender.tender_url,
        "name": tender.metadata.name,
        "organization": tender.metadata.organization,
        "submission_deadline": tender.metadata.submission_deadline,
        "initiation_date": tender.metadata.initiation_date,
        "procedure_type": tender.metadata.procedure_type,
        "source_type": tender.metadata.source_type,
        "files_count": tender.files_count,
        "file_urls": tender.file_urls
    }
