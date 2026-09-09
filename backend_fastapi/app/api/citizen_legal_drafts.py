from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import require_role
from app.models.user import Role, User
from app.schemas.legal_draft import LegalDraftRequest, PdfRequest
from app.services.legal_draft_service import legal_draft_service

router = APIRouter(prefix="/citizen/legal-drafts", tags=["Citizen Legal Drafts"])


@router.post("/generate")
def generate_draft(payload: LegalDraftRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role(Role.CIVILIAN))):
    try:
        return {"success": True, "data": legal_draft_service.generate(db, payload).model_dump()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to generate the draft right now. Please review your information and try again.") from exc


@router.post("/pdf")
def download_pdf(payload: PdfRequest, current_user: User = Depends(require_role(Role.CIVILIAN))):
    try:
        document = legal_draft_service.pdf(payload.draft)
        return StreamingResponse(document, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=nyayaai-legal-draft.pdf"})
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to create the PDF right now. Please try again.") from exc
