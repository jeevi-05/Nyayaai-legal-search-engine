"""Citizen-only eCourtsIndia lawyer discovery endpoints."""

from typing import Any
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, Query

from app.middleware.auth import require_role
from app.models.user import Role, User
from app.services.ecourts_service import ECourtsSearchError, ecourts_service

router = APIRouter(prefix="/citizen/lawyers", tags=["Citizen Lawyer Search"])


@router.get("/search")
def search_lawyers(
    legal_issue: str = Query("", max_length=300), state: str = Query("", max_length=100), district: str = Query("", max_length=100), court: str = Query("", max_length=160), case_type: str = Query("", max_length=100), case_status: str = Query("", max_length=100), practice_area: str = Query("", max_length=100), advocate_name: str = Query("", max_length=160), page: int = Query(1, ge=1, le=1000), page_size: int = Query(10, ge=1, le=25), current_user: User = Depends(require_role(Role.CIVILIAN)),
) -> dict[str, Any]:
    del current_user
    try:
        return ecourts_service.search_cases(locals())
    except ECourtsSearchError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/case/{cnr}")
def get_case(cnr: str, current_user: User = Depends(require_role(Role.CIVILIAN))) -> dict[str, Any]:
    del current_user
    case = ecourts_service.get_case(cnr)
    if not case:
        raise HTTPException(status_code=404, detail="Case details are not available from the current search results.")
    return case


@router.get("/profile/{lawyer_identifier}")
def get_lawyer_profile(lawyer_identifier: str, current_user: User = Depends(require_role(Role.CIVILIAN))) -> dict[str, Any]:
    del current_user
    lawyer = ecourts_service.get_lawyer(unquote(lawyer_identifier))
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer profile could not be found.")
    return lawyer


@router.get("/{lawyer_id}")
def get_lawyer(lawyer_id: str, current_user: User = Depends(require_role(Role.CIVILIAN))) -> dict[str, Any]:
    del current_user
    lawyer = ecourts_service.get_lawyer(lawyer_id)
    if not lawyer:
        lawyer = ecourts_service.get_lawyer(unquote(lawyer_id))
    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer details are available after a related search.")
    return lawyer
