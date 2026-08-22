"""Judge-only judicial intelligence endpoints."""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import require_judge
from app.models.analysis_result import AnalysisResult, AnalysisType
from app.models.judicial_analysis_result import JudicialAnalysisResult, JudicialAnalysisType
from app.models.legal_document import LegalDocument
from app.services.judgment_comparison_service import judgment_comparison_service
from app.services.precedent_analysis_service import precedent_analysis_service
from app.services.legal_reasoning_service import legal_reasoning_service
from app.services.case_law_synthesis_service import case_law_synthesis_service
from app.services.indian_kanoon_service import search_judgments
from app.services.ik_ingestion_service import ingest_ik_result

router = APIRouter(prefix="/judge", tags=["Judicial Intelligence"])


def _save(db: Session, user_id: int, analysis_type: AnalysisType, case_ids: list[str], result: dict) -> None:
    db.add(AnalysisResult(user_id=user_id, analysis_type=analysis_type, case_ids=json.dumps(case_ids), result_json=json.dumps(result)))
    db.add(JudicialAnalysisResult(
        case_id=",".join(case_ids) or "topic",
        analysis_type=JudicialAnalysisType[analysis_type.name],
        result_json=json.dumps(result),
        confidence_score=round(float(result.get("confidence_score", 0.75)), 2),
    ))
    db.commit()


def _document(db: Session, case_id: str):
    doc = db.query(LegalDocument).filter((LegalDocument.external_id == case_id) | (LegalDocument.id == case_id)).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Judgment not found in the repository.")
    return doc


def _ingest_indian_kanoon_matches(db: Session, query: str) -> None:
    """Populate the unbounded local corpus on demand; no fixed seed-case limit."""
    if not query:
        return
    for result in search_judgments(query):
        try:
            ingest_ik_result(db, result)
        except Exception:
            db.rollback()


@router.get("/judgments")
def list_judgments(query: str = "", court: str = "", year: int | None = None, db: Session = Depends(get_db), current_user=Depends(require_judge)):
    if query:
        _ingest_indian_kanoon_matches(db, query)
    statement = db.query(LegalDocument).filter(LegalDocument.judgment_text.isnot(None))
    if query:
        statement = statement.filter(LegalDocument.title.ilike(f"%{query}%"))
    if court:
        statement = statement.filter(LegalDocument.court.ilike(f"%{court}%"))
    if year:
        statement = statement.filter(LegalDocument.year == year)
    docs = statement.order_by(LegalDocument.year.desc()).limit(100).all()
    return {"success": True, "data": [{"id": doc.external_id or str(doc.id), "title": doc.title, "court": doc.court, "year": doc.year, "citation": doc.citation, "bench": doc.judges, "acts_sections": doc.acts_sections} for doc in docs]}


@router.post("/judgment-comparison")
def compare(payload: dict[str, Any], db: Session = Depends(get_db), current_user=Depends(require_judge)):
    case1, case2 = payload.get("case1_id"), payload.get("case2_id")
    if not case1 or not case2 or case1 == case2:
        raise HTTPException(status_code=400, detail="Provide two different judgment IDs.")
    result = judgment_comparison_service.compare_judgments(db, str(case1), str(case2))
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    _save(db, current_user.id, AnalysisType.JUDGMENT_COMPARISON, [str(case1), str(case2)], result)
    return {"success": True, "data": result}


@router.post("/precedent-analysis")
def precedent_analysis(payload: dict[str, Any], db: Session = Depends(get_db), current_user=Depends(require_judge)):
    issue = (payload.get("issue") or payload.get("context") or "").strip()
    if not issue:
        raise HTTPException(status_code=400, detail="A legal issue or case context is required.")
    _ingest_indian_kanoon_matches(db, issue)
    result = precedent_analysis_service.analyze(db, issue)
    _save(db, current_user.id, AnalysisType.PRECEDENT_ANALYSIS, [], result)
    return {"success": True, "data": result}


@router.get("/legal-reasoning/{case_id}")
def legal_reasoning(case_id: str, db: Session = Depends(get_db), current_user=Depends(require_judge)):
    result = legal_reasoning_service.extract(_document(db, case_id))
    _save(db, current_user.id, AnalysisType.LEGAL_REASONING, [case_id], result)
    return {"success": True, "data": result}


@router.post("/case-law-synthesis")
def case_law_synthesis(payload: dict[str, Any], db: Session = Depends(get_db), current_user=Depends(require_judge)):
    topic = (payload.get("topic") or "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="A legal topic is required.")
    _ingest_indian_kanoon_matches(db, topic)
    result = case_law_synthesis_service.synthesize(db, topic)
    _save(db, current_user.id, AnalysisType.CASE_LAW_SYNTHESIS, [], result)
    return {"success": True, "data": result}
