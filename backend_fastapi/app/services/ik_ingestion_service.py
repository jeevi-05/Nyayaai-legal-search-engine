"""
Indian Kanoon Ingestion Service
Orchestrates: download PDF → extract text → summarise → embed → persist.
Reuses existing pdf_processor and embedding_service.
"""

import json
import sys
from loguru import logger
from sqlalchemy.orm import Session

from app.models.legal_document import LegalDocument, DocumentCategory
from app.repositories import document_repository
from app.services.pdf_download_service import download_and_save, generate_pdf_from_text
from app.services.pdf_processor import extract_text, generate_summary
from app.services.embedding_service import EmbeddingService
from app.services.indian_kanoon_service import fetch_document_metadata
from app.services.legal_document_processor import legal_document_processor
from app.services.case_processing_service import process_judgment

_embedding_service = EmbeddingService()

# Configure loguru for compatibility
logger.remove()
logger.add(sys.stderr, level="INFO")


def ingest_ik_result(db: Session, ik_result: dict) -> LegalDocument | None:
    """
    Persist one Indian Kanoon search result into the database.

    Steps:
      1. Skip if already stored (dedup by external_id).
      2. Download or generate PDF from judgment_text.
      3. Extract text from PDF if available.
      4. Generate summary and embedding.
      5. Save LegalDocument row.

    Returns the saved LegalDocument, or None if skipped/failed.
    """
    doc_id = ik_result.get("doc_id", "")
    if not doc_id:
        return None

    # ── 1. Dedup ──────────────────────────────────────────────────────────────
    if document_repository.exists_by_external_id(db, doc_id):
        logger.debug("IK doc_id={} already in DB — skipping", doc_id)
        return document_repository.get_by_external_id(db, doc_id)

    # Always fetch the full document before processing; a search snippet is never
    # used as the canonical judgment text.
    full_metadata = fetch_document_metadata(doc_id) or {}
    title = full_metadata.get("title") or ik_result.get("title", "Untitled")
    snippet = full_metadata.get("snippet") or ik_result.get("snippet", "")
    judgment_text = full_metadata.get("judgment_text", "")
    processed_document = legal_document_processor.process(judgment_text, {**ik_result, **full_metadata})
    case_parts = process_judgment(processed_document["text"])

    # ── 2. Download or generate PDF ────────────────────────────────────────────
    pdf_path = None
    try:
        # First try to get judgment text from IK
        judgment_text = processed_document["text"]
        
        if judgment_text and judgment_text.strip():
            # Always generate PDF from judgment_text (fallback)
            pdf_path = generate_pdf_from_text(title, judgment_text, doc_id)
        else:
            # Try IK download as fallback
            pdf_path = download_and_save(doc_id, title)
    except Exception as e:
        logger.warning("PDF generation failed for doc_id={}: {}", doc_id, e)

    # ── 3. Extract text ───────────────────────────────────────────────────────
    extracted_text = ""
    if pdf_path:
        try:
            extracted_text = extract_text(pdf_path)
        except Exception as e:
            logger.warning("Text extraction failed for {}: {}", pdf_path, e)

    # Fall back to snippet if PDF text unavailable
    text_for_ai = extracted_text or processed_document["text"] or snippet or title

    # ── 4. Summary + embedding ────────────────────────────────────────────────
    summary = generate_summary(text_for_ai)
    embedding = processed_document["embedding"] or _embedding_service.embed(text_for_ai)
    embedding_json = json.dumps(embedding)

    # ── 5. Persist ────────────────────────────────────────────────────────────
    # Use a synthetic source_file so the existing UniqueConstraint is satisfied
    source_file = f"ik_{doc_id}.pdf"

    doc = LegalDocument(
        title          = title,
        case_name      = processed_document["metadata"]["case_name"],
        bench          = processed_document["metadata"]["bench"],
        judgment_date  = processed_document["metadata"]["date"],
        acts           = json.dumps(processed_document["entities"]["acts"]),
        sections       = json.dumps(processed_document["entities"]["sections"]),
        paragraphs     = json.dumps(processed_document["paragraphs"]),
        source_file    = source_file,
        file_path      = pdf_path or source_file,
        category       = DocumentCategory.JUDGMENT,
        description    = snippet,
        citation       = ik_result.get("citation", ""),
        year           = processed_document["metadata"]["year"],
        court          = processed_document["metadata"]["court"],
        source         = "indian_kanoon",
        external_id    = doc_id,
        document_url   = ik_result.get("document_url", ""),
        pdf_path       = pdf_path,
        case_type      = "JUDGMENT",
        file_type      = "PDF" if pdf_path else "JSON",
        extracted_text = extracted_text,
        judgment_text  = processed_document["text"],
        acts_sections  = ", ".join(processed_document["entities"]["acts"] + processed_document["entities"]["sections"]),
        judges         = processed_document["metadata"]["bench"],
        case_facts     = case_parts.get("case_facts", ""),
        legal_issues   = case_parts.get("legal_issues", ""),
        arguments      = case_parts.get("arguments", ""),
        court_reasoning= case_parts.get("court_reasoning", ""),
        final_decision = case_parts.get("final_decision", ""),
        summary        = summary,
        embedding      = embedding_json,
        uploaded_by    = "indian_kanoon",
    )

    try:
        saved = document_repository.create_document(db, doc)
        logger.info("Ingested IK doc_id={} → DB id={}", doc_id, saved.id)
        return saved
    except Exception as e:
        db.rollback()
        logger.error("Failed to save IK doc_id={}: {}", doc_id, e)
        return None


def _fetch_judgment_text(doc_id: str) -> str:
    """Fetch judgment text from Indian Kanoon API."""
    try:
        from app.services.indian_kanoon_service import fetch_document_metadata
        meta = fetch_document_metadata(doc_id)
        return meta.get("judgment_text", "") if meta else ""
    except Exception:
        return ""
