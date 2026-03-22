from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from app.database import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(String, nullable=False)      # "1.0", "1.1", "2.0"
    version_label = Column(String, nullable=True)        # "Rev A", "2024-Q1"
    file_path = Column(String, nullable=False)           # Relative to storage root
    file_name = Column(String, nullable=False)           # Original filename
    file_size = Column(Integer, nullable=False)          # Bytes
    mime_type = Column(String, nullable=False)
    sha256_hash = Column(String, index=True, nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    change_summary = Column(String, nullable=True)
    extracted_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    is_current = Column(Boolean, default=False, index=True)
    relative_folder_path = Column(String, nullable=True)  # webkitRelativePath folder

    document = relationship(
        "Document",
        back_populates="versions",
        foreign_keys=[document_id],
    )
    uploader = relationship("User", back_populates="uploaded_versions")
    comparisons_as_a = relationship(
        "ComparisonResult",
        back_populates="version_a",
        foreign_keys="ComparisonResult.version_a_id",
    )
    comparisons_as_b = relationship(
        "ComparisonResult",
        back_populates="version_b",
        foreign_keys="ComparisonResult.version_b_id",
    )
