from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.comparison import CompareRequest, ComparisonResultResponse
from app.services.comparison_service import compare_versions, get_latest_comparison

router = APIRouter(tags=["comparison"])


@router.post("/comparison/compare", response_model=ComparisonResultResponse)
def compare(
    req: CompareRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        result = compare_versions(req.version_a_id, req.version_b_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/comparison/document/{document_id}/latest", response_model=ComparisonResultResponse)
def latest_comparison(
    document_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = get_latest_comparison(document_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="No comparison available")
    return result
