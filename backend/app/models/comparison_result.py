from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from app.database import Base


class ComparisonResult(Base):
    __tablename__ = "comparison_results"
    __table_args__ = (UniqueConstraint("version_a_id", "version_b_id", name="uq_comparison"),)

    id = Column(Integer, primary_key=True, index=True)
    version_a_id = Column(Integer, ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False)
    version_b_id = Column(Integer, ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False)
    comparison_type = Column(String, nullable=False)   # "text", "bom", "dxf"
    diff_data = Column(JSON, nullable=False)
    summary = Column(String, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)

    version_a = relationship("DocumentVersion", back_populates="comparisons_as_a", foreign_keys=[version_a_id])
    version_b = relationship("DocumentVersion", back_populates="comparisons_as_b", foreign_keys=[version_b_id])
