import asyncio
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.user import User
from app.schemas.document import DocumentResponse, UploadResponse
from app.services import document_service, storage_service

router = APIRouter(tags=["documents"])


@router.get("/projects/{project_id}/documents", response_model=list[DocumentResponse])
def list_documents(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    docs = db.query(Document).filter(Document.project_id == project_id).all()
    result = []
    for doc in docs:
        version_count = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc.id).count()
        schema = DocumentResponse.model_validate(doc)
        schema.version_count = version_count
        if doc.current_version:
            schema.current_version = document_service._version_to_schema(doc.current_version, db)
        result.append(schema)
    return result


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    project_id: int = Form(...),
    doc_type_override: Optional[str] = Form(None),
    doc_name_override: Optional[str] = Form(None),
    change_summary: Optional[str] = Form(None),
    folder_path: Optional[str] = Form(None),
    version_label: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await document_service.process_upload(
        upload=file,
        project_id=project_id,
        uploader_id=current_user.id,
        db=db,
        doc_type_override=doc_type_override,
        doc_name_override=doc_name_override,
        change_summary=change_summary,
        folder_path=folder_path,
        version_label=version_label,
    )


@router.post("/documents/upload-batch", response_model=list[UploadResponse])
async def upload_batch(
    files: list[UploadFile] = File(...),
    project_id: int = Form(...),
    folder_paths: Optional[str] = Form(None),  # JSON array of folder paths
    change_summary: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import json
    paths = json.loads(folder_paths) if folder_paths else [None] * len(files)
    if len(paths) < len(files):
        paths.extend([None] * (len(files) - len(paths)))

    results = []
    for file, folder_path in zip(files, paths):
        result = await document_service.process_upload(
            upload=file,
            project_id=project_id,
            uploader_id=current_user.id,
            db=db,
            folder_path=folder_path,
            change_summary=change_summary,
        )
        results.append(result)
    return results


@router.post("/documents/scan-path", response_model=list[UploadResponse])
async def scan_local_path(
    path: str = Body(..., embed=True),
    project_id: int = Body(..., embed=True),
    change_summary: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Scan a local server-side directory and ingest all supported files."""
    scan_path = Path(path)
    if not scan_path.exists() or not scan_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path not found or not a directory: {path}")

    SUPPORTED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv", ".dxf", ".dwg",
                            ".jpg", ".jpeg", ".png", ".tiff", ".tif"}

    file_paths = [
        p for p in scan_path.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    results = []
    for file_path in file_paths:
        folder_path = str(file_path.parent.relative_to(scan_path))
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            from fastapi import UploadFile
            from io import BytesIO
            fake_upload = UploadFile(filename=file_path.name, file=BytesIO(content))

            result = await document_service.process_upload(
                upload=fake_upload,
                project_id=project_id,
                uploader_id=current_user.id,
                db=db,
                folder_path=folder_path,
                change_summary=change_summary,
            )
            results.append(result)
        except Exception as e:
            pass  # Continue processing other files

    return results


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return document_service._doc_to_schema(doc, db)
