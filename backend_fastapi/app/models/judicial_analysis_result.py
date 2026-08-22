import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, Float, Integer, String, Text
from app.core.database import Base


class JudicialAnalysisType(str, enum.Enum):
    JUDGMENT_COMPARISON = "JUDGMENT_COMPARISON"
    PRECEDENT_ANALYSIS = "PRECEDENT_ANALYSIS"
    LEGAL_REASONING = "LEGAL_REASONING"
    CASE_LAW_SYNTHESIS = "CASE_LAW_SYNTHESIS"


class JudicialAnalysisResult(Base):
    __tablename__ = "judicial_analysis_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=False, index=True)
    analysis_type = Column(Enum(JudicialAnalysisType), nullable=False, index=True)
    result_json = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
