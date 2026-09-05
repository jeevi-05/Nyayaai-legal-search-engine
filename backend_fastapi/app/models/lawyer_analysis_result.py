import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, Float, Integer, String, Text

from app.core.database import Base


class LawyerAnalysisType(str, enum.Enum):
    ADVANCED_RESEARCH = "ADVANCED_RESEARCH"
    ARGUMENT_RESEARCH = "ARGUMENT_RESEARCH"
    CITATION_FINDER = "CITATION_FINDER"
    CASE_BRIEF = "CASE_BRIEF"


class LawyerAnalysisResult(Base):
    """Cached advocate-research output. Results remain scoped to the requesting lawyer."""

    __tablename__ = "lawyer_analysis_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    case_id = Column(String, nullable=True, index=True)
    analysis_type = Column(Enum(LawyerAnalysisType), nullable=False, index=True)
    query = Column(Text, nullable=True)
    result_json = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
