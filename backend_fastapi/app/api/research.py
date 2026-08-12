import json
import os
import sys
import logging

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.legal_document import LegalDocument, DocumentCategory
from app.repositories import document_repository
from app.services.semantic_search_service import semantic_search_service
from app.services.decision_support_service import decision_support_service
from app.services import indian_kanoon_service
from app.services.ik_ingestion_service import ingest_ik_result
from app.services.case_processing_service import process_judgment
from app.services.pdf_download_service import download_and_save, generate_pdf_from_text
from app.services.pdf_processor import extract_text, generate_summary
from app.services.embedding_service import EmbeddingService

router = APIRouter(
    prefix="/research",
    tags=["Legal Research"]
)

_embedding_service = EmbeddingService()
logger = logging.getLogger(__name__)

# Configure loguru for compatibility
from loguru import logger as loguru_logger
loguru_logger.remove()
loguru_logger.add(sys.stderr, level="INFO")


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/research/search  (existing — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/search")
def search_cases(
    query: str,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Unified legal search:
      Step 1 — Semantic search across local SQLite database.
      Step 2 — Call Indian Kanoon API.
      Step 3 — Ingest new IK results into DB in the background.
      Step 4 — Merge and deduplicate by title similarity.
      Step 5 — Return combined ranked results.
    """
    local_results = semantic_search_service.search(db, query, top_k=10)
    ik_raw        = indian_kanoon_service.search_judgments(query)

    if ik_raw:
        background_tasks.add_task(_ingest_ik_results, db, ik_raw)

    ik_results = [_ik_to_result(r) for r in ik_raw]
    combined   = _merge_and_deduplicate(local_results, ik_results)

    return {"success": True, "query": query, "results": combined}


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/research/case/{external_id}
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/case/{external_id}")
def get_case_detail(
    external_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Fetch complete judgment details.

    Flow:
      1. Check local DB by external_id.
         - If found AND judgment_text is populated → return immediately.
         - If found but judgment_text is empty → enrich from IK then return.
      2. If not in DB → fetch from Indian Kanoon, process, persist, return.
    """
    doc = document_repository.get_by_external_id(db, external_id)

    # ── Case already fully processed ─────────────────────────────────────────
    if doc and doc.judgment_text and doc.case_facts:
        ai_analysis = decision_support_service.analyze(doc, doc.title)
        similar = _get_similar(db, doc)
        detail = _doc_to_detail(doc)
        detail["ai_analysis"]   = ai_analysis
        detail["similar_cases"] = similar
        return {"success": True, "data": detail}

    # ── Fetch full detail from Indian Kanoon ──────────────────────────────────
    ik_data = indian_kanoon_service.fetch_document_metadata(external_id)

    if not ik_data:
        # IK unavailable — return whatever we have locally
        if doc:
            return {"success": True, "data": _doc_to_detail(doc)}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found in local database or Indian Kanoon.",
        )

    judgment_text = ik_data.get("judgment_text", "")
    processed     = process_judgment(judgment_text)

    # ── Persist or update ─────────────────────────────────────────────────────
    if doc:
        # Enrich existing row
        doc.judgment_text  = judgment_text
        doc.acts_sections  = processed["acts_sections"] or ik_data.get("acts_sections", "")
        doc.judges         = processed["judges"]        or ik_data.get("judges", "")
        doc.case_facts     = processed["case_facts"]
        doc.legal_issues   = processed["legal_issues"]
        doc.arguments      = processed["arguments"]
        doc.court_reasoning= processed["court_reasoning"]
        doc.final_decision = processed["final_decision"]
        doc.citation       = doc.citation or ik_data.get("citation", "")
        doc.court          = doc.court    or ik_data.get("court", "")
        doc.year           = doc.year     or ik_data.get("year")
        doc.document_url   = ik_data.get("document_url", "")
        # Re-embed with full text if we now have it
        if judgment_text and not doc.embedding:
            emb = _embedding_service.embed(judgment_text[:4000])
            doc.embedding = json.dumps(emb)
        db.commit()
        db.refresh(doc)
    else:
        # Create new row
        source_file = f"ik_{external_id}.pdf"
        emb         = _embedding_service.embed(judgment_text[:4000] if judgment_text else ik_data.get("snippet", ""))
        doc = LegalDocument(
            title          = ik_data.get("title", "Untitled"),
            source_file    = source_file,
            file_path      = source_file,
            category       = DocumentCategory.JUDGMENT,
            description    = ik_data.get("snippet", ""),
            citation       = ik_data.get("citation", ""),
            year           = ik_data.get("year"),
            court          = ik_data.get("court", ""),
            source         = "indian_kanoon",
            external_id    = external_id,
            document_url   = ik_data.get("document_url", ""),
            case_type      = "JUDGMENT",
            file_type      = "JSON",
            judgment_text  = judgment_text,
            acts_sections  = processed["acts_sections"] or ik_data.get("acts_sections", ""),
            judges         = processed["judges"]        or ik_data.get("judges", ""),
            case_facts     = processed["case_facts"],
            legal_issues   = processed["legal_issues"],
            arguments      = processed["arguments"],
            court_reasoning= processed["court_reasoning"],
            final_decision = processed["final_decision"],
            extracted_text = judgment_text,
            summary        = generate_summary(judgment_text),
            embedding      = json.dumps(emb),
            uploaded_by    = "indian_kanoon",
        )
        doc = document_repository.create_document(db, doc)

    # ── AI analysis ───────────────────────────────────────────────────────────
    ai_analysis = decision_support_service.analyze(doc, doc.title)

    # ── Similar cases ─────────────────────────────────────────────────────────
    similar = []
    if doc.embedding:
        try:
            emb_vec = json.loads(doc.embedding)
            similar = semantic_search_service.search_similar_documents(
                db, emb_vec, doc.id, top_k=5
            )
        except Exception:
            pass

    detail = _doc_to_detail(doc)
    detail["ai_analysis"] = ai_analysis
    detail["similar_cases"] = similar

    return {"success": True, "data": detail}


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/research/case/{external_id}/download
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/case/{external_id}/download")
def download_case_pdf(
    external_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Download the PDF for a case by its Indian Kanoon external_id.
    Checks local pdf_path first; downloads/generates from IK if not cached.
    Returns 200 with PDF, 404 if case not found, 500 on generation failure.
    """
    doc = document_repository.get_by_external_id(db, external_id)

    if not doc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Case not found in database.",
                "details": f"No case found with external_id: {external_id}",
                "data": None,
            },
        )

    # Check cached path first
    if doc.pdf_path and os.path.isfile(doc.pdf_path):
        return FileResponse(
            path=doc.pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(doc.pdf_path),
        )

    # Generate PDF from judgment_text (fallback - always available for processed cases)
    title = doc.title or external_id
    judgment_text = doc.judgment_text or ""
    
    if not judgment_text.strip():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Judgment text not available for PDF generation.",
                "details": "The case judgment text is empty or missing.",
                "data": None,
            },
        )

    try:
        pdf_path = generate_pdf_from_text(title, judgment_text, external_id)
        
        if not pdf_path:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "message": "PDF generation failed.",
                    "details": "Failed to generate PDF from judgment text. Check server logs for details.",
                    "data": None,
                },
            )
        
        # Update document with PDF path
        doc.pdf_path = pdf_path
        doc.file_type = "PDF"
        db.commit()
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF download failed for {external_id}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Server error while generating PDF.",
                "details": str(e),
                "data": None,
            },
        )


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/research/case/{external_id}/add-to-repository
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/case/{external_id}/add-to-repository")
def add_to_repository(
    external_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Full ingestion pipeline triggered by the frontend 'Add to Repository' button:
      1. Fetch IK metadata (if not already in DB).
      2. Download or generate PDF from judgment_text.
      3. Extract text from PDF.
      4. Generate summary + embedding.
      5. Save / update in legal_documents.
    """
    # Already fully ingested with text and embedding?
    existing = document_repository.get_by_external_id(db, external_id)
    if existing and existing.embedding and existing.case_facts:
        return {
            "success": True,
            "message": "Case already exists in the Legal Repository.",
            "data": {"id": existing.id, "title": existing.title},
        }

    # Fetch metadata
    ik_data = indian_kanoon_service.fetch_document_metadata(external_id)
    if not ik_data:
        raise HTTPException(
            status_code=502,
            detail="Could not fetch case details from Indian Kanoon.",
        )

    title = ik_data.get("title", "Untitled")
    judgment_text = ik_data.get("judgment_text", "")
    
    if not judgment_text.strip():
        raise HTTPException(
            status_code=404,
            detail="Judgment text not available for this case.",
        )

    # Generate PDF from judgment_text (fallback - always available for processed cases)
    pdf_path = generate_pdf_from_text(title, judgment_text, external_id)
    
    if not pdf_path:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF from judgment text.",
        )

    # Extract text from PDF
    extracted_text = ""
    try:
        extracted_text = extract_text(pdf_path)
    except Exception:
        extracted_text = judgment_text  # Fallback to judgment_text

    text_for_ai = extracted_text or judgment_text or ik_data.get("snippet", title)
    summary = generate_summary(text_for_ai)
    emb = _embedding_service.embed(text_for_ai[:4000])
    embedding_json = json.dumps(emb)
    processed = process_judgment(text_for_ai)

    if existing:
        existing.pdf_path = pdf_path
        existing.extracted_text = extracted_text
        existing.summary = summary
        existing.embedding = embedding_json
        existing.judgment_text = judgment_text
        existing.acts_sections = processed["acts_sections"]
        existing.judges = processed["judges"]
        existing.case_facts = processed["case_facts"]
        existing.legal_issues = processed["legal_issues"]
        existing.arguments = processed["arguments"]
        existing.court_reasoning = processed["court_reasoning"]
        existing.final_decision = processed["final_decision"]
        existing.file_type = "PDF"
        db.commit()
        db.refresh(existing)
        saved = existing
    else:
        source_file = f"ik_{external_id}.pdf"
        doc = LegalDocument(
            title=title,
            source_file=source_file,
            file_path=pdf_path or source_file,
            category=DocumentCategory.JUDGMENT,
            description=ik_data.get("snippet", ""),
            citation=ik_data.get("citation", ""),
            year=ik_data.get("year"),
            court=ik_data.get("court", ""),
            source="indian_kanoon",
            external_id=external_id,
            document_url=ik_data.get("document_url", ""),
            pdf_path=pdf_path,
            case_type="JUDGMENT",
            file_type="PDF",
            extracted_text=extracted_text,
            summary=summary,
            embedding=embedding_json,
            judgment_text=judgment_text,
            acts_sections=processed["acts_sections"],
            judges=processed["judges"],
            case_facts=processed["case_facts"],
            legal_issues=processed["legal_issues"],
            arguments=processed["arguments"],
            court_reasoning=processed["court_reasoning"],
            final_decision=processed["final_decision"],
            uploaded_by=current_user.email,
        )
        saved = document_repository.create_document(db, doc)

    return {
        "success": True,
        "message": "Case added successfully to Legal Repository.",
        "data": {"id": saved.id, "title": saved.title},
    }


# ── Private helpers ───────────────────────────────────────────────────────────

def _get_similar(db, doc) -> list:
    """Return similar cases using stored embedding."""
    if not doc.embedding:
        return []
    try:
        emb_vec = json.loads(doc.embedding)
        return semantic_search_service.search_similar_documents(db, emb_vec, doc.id, top_k=5)
    except Exception:
        return []


def _ingest_ik_results(db: Session, ik_raw: list[dict]) -> None:
    for item in ik_raw:
        try:
            ingest_ik_result(db, item)
        except Exception:
            pass


def _ik_to_result(r: dict) -> dict:
    return {
        "id":           None,
        "title":        r.get("title", ""),
        "category":     "JUDGMENT",
        "year":         r.get("year"),
        "court":        r.get("court", ""),
        "citation":     r.get("citation", ""),
        "description":  r.get("snippet", ""),
        "summary":      r.get("snippet", ""),
        "similarity":   0.0,
        "match_reason": "Result from Indian Kanoon legal database.",
        "source":       "indian_kanoon",
        "document_url": r.get("document_url", ""),
        "doc_id":       r.get("doc_id", ""),
        "decision_support": {
            "recommendation":    "Refer to the full judgment on Indian Kanoon.",
            "precedent_strength": "MEDIUM",
        },
    }


def _merge_and_deduplicate(local, ik, max_results=15):
    seen = {_norm(r["title"]) for r in local}
    unique_ik = [r for r in ik if _norm(r["title"]) not in seen]
    return (local + unique_ik)[:max_results]


def _norm(title: str) -> str:
    import re
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def _doc_to_detail(doc: LegalDocument) -> dict:
    return {
        "id":             doc.id,
        "external_id":    doc.external_id,
        "title":          doc.title,
        "court":          doc.court,
        "year":           doc.year,
        "citation":       doc.citation,
        "source":         doc.source,
        "document_url":   doc.document_url,
        "judges":         doc.judges,
        "description":    doc.description,
        "summary":        doc.summary,
        "judgment_text":  doc.judgment_text,
        "acts_sections":  doc.acts_sections,
        "case_facts":     doc.case_facts,
        "legal_issues":   doc.legal_issues,
        "arguments":      doc.arguments,
        "court_reasoning":doc.court_reasoning,
        "final_decision": doc.final_decision,
        "pdf_path":       doc.pdf_path,
        "tags":           doc.tags,
        "category":       doc.category.value if doc.category else None,
    }
