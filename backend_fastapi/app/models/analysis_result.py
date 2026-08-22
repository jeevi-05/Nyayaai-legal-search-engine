import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text

from app.core.database import Base


class AnalysisType(str, enum.Enum):
    JUDGMENT_COMPARISON = "JUDGMENT_COMPARISON"
    PRECEDENT_ANALYSIS = "PRECEDENT_ANALYSIS"
    LEGAL_REASONING = "LEGAL_REASONING"
    CASE_LAW_SYNTHESIS = "CASE_LAW_SYNTHESIS"


class AnalysisResult(Base):
    """Persisted judicial-intelligence output, scoped to the requesting user."""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    analysis_type = Column(Enum(AnalysisType), nullable=False, index=True)
    case_ids = Column(Text, nullable=True)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
