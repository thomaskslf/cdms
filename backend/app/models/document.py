import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class DocType(str, enum.Enum):
    zeichnung = "zeichnung"
    stückliste = "stückliste"
    bestückzeichnung = "bestückzeichnung"
    montagezeichnung = "montagezeichnung"
    key_anweisung = "key_anweisung"
    unterbaugruppe = "unterbaugruppe"


class DocumentStatus(str, enum.Enum):
    current = "current"
    outdated = "outdated"
    needs_review = "needs_review"


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (UniqueConstraint("project_id", "doc_type", "name", name="uq_document"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(Enum(DocType), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    current_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.current)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="documents")
    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        foreign_keys="DocumentVersion.document_id",
        cascade="all, delete-orphan",
    )
    current_version = relationship(
        "DocumentVersion",
        foreign_keys=[current_version_id],
        post_update=True,
    )
