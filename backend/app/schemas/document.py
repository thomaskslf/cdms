from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

from app.models.document import DocType, DocumentStatus


class DocumentVersionResponse(BaseModel):
    id: int
    document_id: int
    version_number: str
    version_label: Optional[str]
    file_name: str
    file_size: int
    mime_type: str
    uploader_id: int
    uploader_username: Optional[str] = None
    uploaded_at: datetime
    change_summary: Optional[str]
    is_current: bool
    thumbnail_path: Optional[str]

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: int
    project_id: int
    doc_type: DocType
    name: str
    description: Optional[str]
    status: DocumentStatus
    current_version_id: Optional[int]
    current_version: Optional[DocumentVersionResponse]
    created_at: datetime
    version_count: int = 0

    model_config = {"from_attributes": True}


class ClassificationResult(BaseModel):
    doc_type: DocType
    confidence: float
    needs_override: bool


class UploadResponse(BaseModel):
    version: DocumentVersionResponse
    document: DocumentResponse
    classification: ClassificationResult
    is_duplicate: bool = False
    auto_comparison_id: Optional[int] = None
