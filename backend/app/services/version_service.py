"""
Version numbering and matching logic.
Format: MAJOR.MINOR (e.g. "1.0", "1.1", "2.0")
"""
import difflib
from typing import Optional

from sqlalchemy.orm import Session

from app.models.document import Document, DocType, DocumentStatus
from app.models.document_version import DocumentVersion

MAJOR_CHANGE_THRESHOLD = 0.30  # >30% similarity drop triggers major increment


def _parse_version(version_str: str) -> tuple[int, int]:
    parts = version_str.split(".")
    return int(parts[0]), int(parts[1] if len(parts) > 1 else 0)


def compute_next_version(document_id: int, db: Session, is_major_change: bool = False) -> str:
    versions = (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .all()
    )
    if not versions:
        return "1.0"

    max_major, max_minor = max(_parse_version(v.version_number) for v in versions)
    if is_major_change:
        return f"{max_major + 1}.0"
    return f"{max_major}.{max_minor + 1}"


def set_current_version(document: Document, version: DocumentVersion, db: Session) -> None:
    # Unset all other versions
    db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document.id,
        DocumentVersion.id != version.id,
    ).update({"is_current": False})

    version.is_current = True
    document.current_version_id = version.id
    document.status = DocumentStatus.current
    db.flush()


def get_or_create_document(
    project_id: int,
    doc_type: str,
    name: str,
    db: Session,
    description: Optional[str] = None,
) -> Document:
    doc = (
        db.query(Document)
        .filter(
            Document.project_id == project_id,
            Document.doc_type == doc_type,
            Document.name == name,
        )
        .first()
    )
    if not doc:
        doc = Document(
            project_id=project_id,
            doc_type=doc_type,
            name=name,
            description=description,
        )
        db.add(doc)
        db.flush()
    return doc


def detect_existing_document(
    filename: str,
    project_id: int,
    doc_type: str,
    db: Session,
) -> Optional[Document]:
    """
    Try to find an existing document this file is likely a new version of.
    Uses filename similarity (SequenceMatcher ratio > 0.75).
    """
    documents = (
        db.query(Document)
        .filter(Document.project_id == project_id, Document.doc_type == doc_type)
        .all()
    )

    best_doc = None
    best_ratio = 0.75  # Minimum threshold

    clean_filename = _strip_version_suffix(filename.lower())

    for doc in documents:
        # Compare against existing version filenames
        versions = (
            db.query(DocumentVersion)
            .filter(DocumentVersion.document_id == doc.id)
            .all()
        )
        for v in versions:
            clean_existing = _strip_version_suffix(v.file_name.lower())
            ratio = difflib.SequenceMatcher(None, clean_filename, clean_existing).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_doc = doc

        # Also compare against the document name
        ratio = difflib.SequenceMatcher(None, clean_filename, doc.name.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_doc = doc

    return best_doc


def _strip_version_suffix(name: str) -> str:
    """Remove common version indicators from filename for comparison."""
    import re
    # Remove extension
    name = re.sub(r"\.[a-z]{2,5}$", "", name)
    # Remove version patterns like _v1, _rev_a, _2024, -v2, Rev.A
    name = re.sub(r"[_\-\s]?(?:v\d+|rev[_\s]?[a-z\d]+|\d{4}|\d+\.\d+)$", "", name, flags=re.IGNORECASE)
    return name.strip()
