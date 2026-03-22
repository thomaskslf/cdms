from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.user import User
from app.schemas.document import DocumentVersionResponse
from app.services import document_service
from app.services.version_service import set_current_version
from app.services.storage_service import get_storage_root

router = APIRouter(tags=["versions"])


@router.get("/documents/{document_id}/versions", response_model=list[DocumentVersionResponse])
def list_versions(document_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    versions = (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.uploaded_at.desc())
        .all()
    )
    return [document_service._version_to_schema(v, db) for v in versions]


@router.get("/versions/{version_id}", response_model=DocumentVersionResponse)
def get_version(version_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    v = db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    return document_service._version_to_schema(v, db)


@router.get("/versions/{version_id}/download")
def download_version(version_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    v = db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    file_path = get_storage_root() / v.file_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(
        path=str(file_path),
        filename=v.file_name,
        media_type=v.mime_type,
    )


@router.post("/versions/{version_id}/set-current")
def set_as_current(version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    doc = db.query(Document).filter(Document.id == v.document_id).first()
    set_current_version(doc, v, db)
    db.commit()
    return {"message": f"Version {v.version_number} is now current"}


@router.delete("/versions/{version_id}", status_code=204)
def delete_version(version_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = db.query(DocumentVersion).filter(DocumentVersion.id == version_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    if v.is_current:
        raise HTTPException(status_code=400, detail="Cannot delete current version. Set another version as current first.")
    if not current_user.is_admin and v.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this version")
    db.delete(v)
    db.commit()
