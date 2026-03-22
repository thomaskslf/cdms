from typing import Optional
from sqlalchemy.orm import Session

from app.comparators.registry import get_comparator
from app.models.comparison_result import ComparisonResult
from app.models.document_version import DocumentVersion


def compare_versions(version_a_id: int, version_b_id: int, db: Session) -> ComparisonResult:
    # Ensure consistent ordering (smaller id first for cache key)
    a_id, b_id = sorted([version_a_id, version_b_id])

    # Check cache
    cached = (
        db.query(ComparisonResult)
        .filter(ComparisonResult.version_a_id == a_id, ComparisonResult.version_b_id == b_id)
        .first()
    )
    if cached:
        return cached

    v_a = db.query(DocumentVersion).filter(DocumentVersion.id == a_id).first()
    v_b = db.query(DocumentVersion).filter(DocumentVersion.id == b_id).first()

    if not v_a or not v_b:
        raise ValueError("Version not found")

    doc = v_a.document
    comparator = get_comparator(doc.doc_type.value, v_a.mime_type, v_b.mime_type)
    output = comparator.compare(v_a, v_b)

    result = ComparisonResult(
        version_a_id=a_id,
        version_b_id=b_id,
        comparison_type=output.comparison_type,
        diff_data=output.diff_data,
        summary=output.summary,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_latest_comparison(document_id: int, db: Session) -> Optional[ComparisonResult]:
    """Compare current version against its predecessor, if exists."""
    from app.models.document import Document

    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not doc.current_version_id:
        return None

    versions = (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.uploaded_at.desc())
        .all()
    )
    if len(versions) < 2:
        return None

    current = versions[0]
    previous = versions[1]
    return compare_versions(current.id, previous.id, db)
