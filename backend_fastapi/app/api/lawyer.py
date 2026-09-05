"""LAWYER-only AI legal research endpoints."""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import require_role
from app.models.lawyer_analysis_result import LawyerAnalysisResult, LawyerAnalysisType
from app.models.user import Role, User
from app.services.argument_research_service import argument_research_service
from app.services.case_brief_service import case_brief_service
from app.services.citation_service import citation_service
from app.services.legal_research_service import legal_research_service

router = APIRouter(prefix="/lawyer", tags=["Advocate AI Research"])


def _save(db: Session, user: User, analysis_type: LawyerAnalysisType, query: str, result: dict, case_id: str | None = None) -> None:
    db.add(LawyerAnalysisResult(
        user_id=user.id, case_id=case_id, analysis_type=analysis_type, query=query,
        result_json=json.dumps(result), confidence_score=float(result.get("confidence_score", 0)),
    ))
    db.commit()


@router.post("/advanced-research")
def advanced_research(payload: dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(require_role(Role.LAWYER))):
    query = (payload.get("query") or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="An advocate research query is required.")
    filters = payload.get("filters") or {}
    filters.update({key: payload[key] for key in ("court", "section") if payload.get(key)})
    if payload.get("year"):
        filters["year_from"] = payload["year"]
        filters["year_to"] = payload["year"]
    result = legal_research_service.research(db, query, filters)
    _save(db, current_user, LawyerAnalysisType.ADVANCED_RESEARCH, query, result)
    return {"success": True, "data": result}


@router.post("/argument-research")
def argument_research(payload: dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(require_role(Role.LAWYER))):
    argument = payload.get("argument") or payload
    if isinstance(argument, dict) and not any((argument.get(key) or "").strip() for key in ("case_issue", "legal_argument")):
        raise HTTPException(status_code=400, detail="A case issue or legal argument is required.")
    if isinstance(argument, str) and not argument.strip():
        raise HTTPException(status_code=400, detail="An argument is required.")
    result = argument_research_service.analyze(db, argument)
    saved_query = argument if isinstance(argument, str) else (argument.get("legal_argument") or argument.get("case_issue") or "")
    _save(db, current_user, LawyerAnalysisType.ARGUMENT_RESEARCH, saved_query, result)
    return {"success": True, "data": result}


@router.post("/citation-finder")
def citation_finder(payload: dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(require_role(Role.LAWYER))):
    proposition = payload.get("proposition") or payload
    if isinstance(proposition, dict) and not (proposition.get("legal_statement") or "").strip():
        raise HTTPException(status_code=400, detail="A legal statement or proposition is required.")
    if isinstance(proposition, str) and not proposition.strip():
        raise HTTPException(status_code=400, detail="A legal proposition is required.")
    result = citation_service.find(db, proposition)
    saved_query = proposition if isinstance(proposition, str) else proposition.get("legal_statement", "")
    _save(db, current_user, LawyerAnalysisType.CITATION_FINDER, saved_query, result)
    return {"success": True, "data": result}


@router.get("/case-brief/{case_id}")
def case_brief(case_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role(Role.LAWYER))):
    result = case_brief_service.generate(db, case_id)
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    _save(db, current_user, LawyerAnalysisType.CASE_BRIEF, case_id, result, case_id)
    return {"success": True, "data": result}


@router.post("/case-similarity")
def case_similarity(payload: dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(require_role(Role.LAWYER))):
    if not (payload.get("case_facts") or "").strip() or not (payload.get("legal_issue") or "").strip():
        raise HTTPException(status_code=400, detail="Case facts and legal issue are required.")
    try:
        result = case_brief_service.compare(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _save(db, current_user, LawyerAnalysisType.CASE_BRIEF, payload["legal_issue"], result)
    return {"success": True, "data": result}
