from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.activity_log import ActivityLog
from app.models.customer import Customer
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.project import Project
from app.models.user import User

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats")
def get_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return {
        "customers": db.query(Customer).count(),
        "projects": db.query(Project).count(),
        "documents": db.query(Document).count(),
        "versions": db.query(DocumentVersion).count(),
    }


@router.get("/dashboard/activity")
def get_activity(limit: int = 20, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    logs = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )
    result = []
    for log in logs:
        entry = {
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "created_at": log.created_at.isoformat(),
            "metadata": log.metadata_,
            "username": log.user.username if log.user else "System",
        }
        result.append(entry)
    return result
