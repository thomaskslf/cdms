"""
Central orchestrator for the document upload pipeline.
Handles single files, folder-batch uploads, and local path scans.
"""
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.extractors import registry as extractor_registry
from app.models.activity_log import ActivityLog
from app.models.document_version import DocumentVersion
from app.schemas.document import ClassificationResult, UploadResponse
from app.services import (
    classification_service,
    comparison_service,
    storage_service,
    version_service,
)


async def process_upload(
    upload: UploadFile,
    project_id: int,
    uploader_id: int,
    db: Session,
    doc_type_override: Optional[str] = None,
    doc_name_override: Optional[str] = None,
    change_summary: Optional[str] = None,
    folder_path: Optional[str] = None,  # webkitRelativePath folder portion
    version_label: Optional[str] = None,
) -> UploadResponse:
    filename = upload.filename or "unknown"
    mime_type = storage_service.detect_mime_type(Path(filename), filename)

    # -- Step 1: Temp save to compute SHA256 --
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
        content = await upload.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        import hashlib
        sha256 = hashlib.sha256(content).hexdigest()
        file_size = len(content)

        # -- Step 2: Duplicate check --
        existing_version = (
            db.query(DocumentVersion).filter(DocumentVersion.sha256_hash == sha256).first()
        )
        if existing_version:
            doc = existing_version.document
            from app.schemas.document import DocumentVersionResponse, DocumentResponse
            return UploadResponse(
                version=_version_to_schema(existing_version, db),
                document=_doc_to_schema(doc, db),
                classification=ClassificationResult(
                    doc_type=doc.doc_type,
                    confidence=1.0,
                    needs_override=False,
                ),
                is_duplicate=True,
            )

        # -- Step 3: Extract text/data --
        extraction = extractor_registry.extract(tmp_path, mime_type)

        # -- Step 4: Classify --
        if doc_type_override:
            detected_type = doc_type_override
            confidence = 1.0
        else:
            detected_type, confidence = classification_service.classify_document(
                filename=filename,
                mime_type=mime_type,
                folder_path=folder_path,
                extracted_text=extraction.text,
            )

        needs_override = confidence < classification_service.CONFIDENCE_THRESHOLD

        # -- Step 5: Get or create Document record --
        doc_name = doc_name_override or _infer_doc_name(filename)
        existing_doc = version_service.detect_existing_document(filename, project_id, detected_type, db)
        if existing_doc:
            doc = existing_doc
        else:
            doc = version_service.get_or_create_document(project_id, detected_type, doc_name, db)

        # -- Step 6: Compute version number --
        is_major = False
        if doc.current_version_id:
            prev_version = db.query(DocumentVersion).filter(
                DocumentVersion.id == doc.current_version_id
            ).first()
            if prev_version and extraction.text and prev_version.extracted_text:
                import difflib
                sim = difflib.SequenceMatcher(None, prev_version.extracted_text, extraction.text).ratio()
                is_major = sim < (1.0 - version_service.MAJOR_CHANGE_THRESHOLD)

        version_number = version_service.compute_next_version(doc.id, db, is_major)

        # -- Step 7: Persist file to final storage location (needs version id first) --
        # Create version record with placeholder path
        version = DocumentVersion(
            document_id=doc.id,
            version_number=version_number,
            version_label=version_label,
            file_path="pending",
            file_name=filename,
            file_size=file_size,
            mime_type=mime_type,
            sha256_hash=sha256,
            uploader_id=uploader_id,
            change_summary=change_summary,
            extracted_text=extraction.text or None,
            extracted_data=extraction.structured_data or None,
            relative_folder_path=folder_path,
        )
        db.add(version)
        db.flush()  # Get version.id

        # Now save to final path
        version_dir = storage_service.get_version_dir(
            doc.project.customer_id, project_id, detected_type, version.id
        )
        ext = Path(filename).suffix.lower()
        final_path = version_dir / f"original{ext}"
        final_path.write_bytes(content)

        version.file_path = str(final_path.relative_to(storage_service.get_storage_root()))

        # -- Step 8: Generate thumbnail --
        thumb = storage_service.generate_thumbnail(final_path, version_dir, mime_type)
        if thumb:
            version.thumbnail_path = str(thumb.relative_to(storage_service.get_storage_root()))

        # -- Step 9: Set as current version --
        version_service.set_current_version(doc, version, db)
        db.commit()
        db.refresh(version)
        db.refresh(doc)

        # -- Step 10: Auto-compare with previous version --
        auto_comparison_id = None
        try:
            comp = comparison_service.get_latest_comparison(doc.id, db)
            if comp:
                auto_comparison_id = comp.id
        except Exception:
            pass

        # -- Step 11: Activity log --
        log = ActivityLog(
            user_id=uploader_id,
            action="upload",
            entity_type="document_version",
            entity_id=version.id,
            metadata_={"filename": filename, "version": version_number, "doc_type": detected_type},
        )
        db.add(log)
        db.commit()

        return UploadResponse(
            version=_version_to_schema(version, db),
            document=_doc_to_schema(doc, db),
            classification=ClassificationResult(
                doc_type=detected_type,
                confidence=confidence,
                needs_override=needs_override,
            ),
            is_duplicate=False,
            auto_comparison_id=auto_comparison_id,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _infer_doc_name(filename: str) -> str:
    """Strip extension and clean up version suffixes for a human-readable name."""
    import re
    name = Path(filename).stem
    name = re.sub(r"[_\-\s]?(?:v\d+|rev[_\s]?[a-z\d]+|\d{4})$", "", name, flags=re.IGNORECASE)
    return name.strip().replace("_", " ").replace("-", " ").title()


def _version_to_schema(v: DocumentVersion, db: Session):
    from app.schemas.document import DocumentVersionResponse
    from app.models.user import User
    user = db.query(User).filter(User.id == v.uploader_id).first()
    data = DocumentVersionResponse.model_validate(v)
    data.uploader_username = user.username if user else None
    return data


def _doc_to_schema(doc, db: Session):
    from app.schemas.document import DocumentResponse
    version_count = db.query(DocumentVersion).filter(DocumentVersion.document_id == doc.id).count()
    data = DocumentResponse.model_validate(doc)
    data.version_count = version_count
    if doc.current_version:
        data.current_version = _version_to_schema(doc.current_version, db)
    return data
