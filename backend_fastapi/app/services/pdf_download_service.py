"""
PDF Download Service
====================
1. Try to download PDF from Indian Kanoon.
2. If unavailable, generate a PDF from judgment text using reportlab.
"""

import os
import re
import sys
from loguru import logger
from app.core.config import get_settings
from app.services.indian_kanoon_service import fetch_document_pdf_bytes

settings = get_settings()

# Configure loguru for compatibility
logger.remove()
logger.add(sys.stderr, level="INFO")

# Production-safe dependency import
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    logger.error("reportlab dependency missing: {}", e)


def download_and_save(doc_id: str, title: str, judgment_text: str = "") -> str | None:
    """
    Returns a local PDF file path.
    Tries IK download first; falls back to generating from text.
    Returns None only if both fail AND no text is available.
    """
    if not REPORTLAB_AVAILABLE:
        logger.error("PDF generation failed: reportlab not installed")
        return None
    
    folder = os.path.join(settings.UPLOAD_DIR, "judgment")
    os.makedirs(folder, exist_ok=True)

    safe   = _safe_filename(title)
    fpath  = os.path.join(folder, f"{safe}_{doc_id}.pdf")

    # Already cached
    if os.path.isfile(fpath):
        logger.info("PDF already cached: {}", fpath)
        return fpath

    # Try IK download
    pdf_bytes = fetch_document_pdf_bytes(doc_id)
    if pdf_bytes:
        with open(fpath, "wb") as f:
            f.write(pdf_bytes)
        logger.info("Saved IK PDF: {}", fpath)
        return fpath

    # Generate from text - ALWAYS generate if judgment_text is available
    if judgment_text and judgment_text.strip():
        generated = _generate_pdf(fpath, title, judgment_text)
        if generated:
            logger.info("Generated PDF from text: {}", fpath)
            return fpath

    logger.warning("No PDF available for doc_id={} and no judgment_text", doc_id)
    return None


def generate_pdf_from_text(title: str, text: str, doc_id: str) -> str | None:
    """Public helper — generate and save a PDF, return path."""
    if not REPORTLAB_AVAILABLE:
        logger.error("PDF generation failed: reportlab not installed")
        return None
    
    folder = os.path.join(settings.UPLOAD_DIR, "judgment")
    os.makedirs(folder, exist_ok=True)
    safe  = _safe_filename(title)
    fpath = os.path.join(folder, f"{safe}_{doc_id}.pdf")
    if _generate_pdf(fpath, title, text):
        return fpath
    return None


# ── Internal ──────────────────────────────────────────────────────────────────

def _generate_pdf(file_path: str, title: str, text: str) -> bool:
    """Use reportlab to write a structured PDF. Returns True on success."""
    if not REPORTLAB_AVAILABLE:
        logger.error("PDF generation failed: reportlab not installed")
        return False
    
    try:
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            leftMargin=2.5 * cm,
            rightMargin=2.5 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CaseTitle",
            parent=styles["Heading1"],
            fontSize=13,
            textColor=colors.HexColor("#1e3a5f"),
            spaceAfter=12,
            alignment=TA_CENTER,
        )
        section_title_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontSize=10,
            textColor=colors.HexColor("#1e3a5f"),
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_LEFT,
        )
        body_style = ParagraphStyle(
            "CaseBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=14,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
        )
        watermark_style = ParagraphStyle(
            "Watermark",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )

        story = []
        story.append(Paragraph("NyayaAI Legal Intelligence Platform", watermark_style))
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(_escape(title), title_style))
        story.append(Spacer(1, 0.5 * cm))

        # Parse judgment text to extract metadata and sections
        sections = _parse_judgment_for_pdf(text)

        # Add structured sections
        for section_name, section_text in sections.items():
            if section_text and section_text.strip():
                story.append(Paragraph(section_name.upper(), section_title_style))
                for para in section_text.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    para = para.replace("\n", " ")
                    try:
                        story.append(Paragraph(_escape(para), body_style))
                        story.append(Spacer(1, 0.2 * cm))
                    except Exception:
                        continue
                story.append(Spacer(1, 0.3 * cm))

        # Add complete judgment text as final section
        story.append(Paragraph("COMPLETE JUDGMENT TEXT", section_title_style))
        for para in text.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            para = para.replace("\n", " ")
            try:
                story.append(Paragraph(_escape(para), body_style))
                story.append(Spacer(1, 0.1 * cm))
            except Exception:
                continue

        doc.build(story)
        logger.info("PDF generated successfully: {}", file_path)
        return True

    except Exception as e:
        logger.error("PDF generation failed for {}: {}", file_path, str(e))
        return False


def _parse_judgment_for_pdf(text: str) -> dict:
    """Parse judgment text and extract sections for structured PDF."""
    from app.services.case_processing_service import process_judgment
    
    processed = process_judgment(text)
    
    sections = {}
    
    # Extract metadata from text if possible
    title_match = re.search(r"^([A-Z][^\n]+?)(?:\n|$)", text[:500])
    case_title = title_match.group(1).strip() if title_match else ""
    
    # Extract court info
    court_match = re.search(r"(High Court|Supreme Court|\w+\s+High Court|\w+\s+Court)", text[:1000], re.IGNORECASE)
    court_name = court_match.group(1) if court_match else ""
    
    # Extract date
    date_match = re.search(r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})", text[:1000])
    date_str = date_match.group(1) if date_match else ""
    
    # Extract citation
    citation_match = re.search(r"\d+\s+\w+\s+\d+", text[:1000])
    citation = citation_match.group(0) if citation_match else ""
    
    # Add metadata section
    metadata_lines = []
    if case_title:
        metadata_lines.append(f"Case Title: {case_title}")
    if court_name:
        metadata_lines.append(f"Court: {court_name}")
    if date_str:
        metadata_lines.append(f"Date: {date_str}")
    if citation:
        metadata_lines.append(f"Citation: {citation}")
    
    if metadata_lines:
        sections["Case Metadata"] = "\n".join(metadata_lines)
    
    # Add extracted sections
    if processed.get("acts_sections"):
        sections["Acts and Sections"] = processed["acts_sections"]
    if processed.get("case_facts"):
        sections["Case Facts"] = processed["case_facts"]
    if processed.get("legal_issues"):
        sections["Legal Issues"] = processed["legal_issues"]
    if processed.get("arguments"):
        sections["Arguments"] = processed["arguments"]
    if processed.get("court_reasoning"):
        sections["Court Reasoning"] = processed["court_reasoning"]
    if processed.get("final_decision"):
        sections["Final Judgment"] = processed["final_decision"]
    
    return sections


def _escape(text: str) -> str:
    """Escape XML special chars for reportlab Paragraph."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _clean_filename(name: str, max_len: int = 80) -> str:
    """
    Clean filename by removing HTML artifacts and special characters.
    
    Removes:
    - HTML tags (<b>, </b>, <i>, etc.)
    - Special characters (except spaces, hyphens, underscores)
    - Duplicate spaces
    
    Example:
        "Section_5_in_The_Protection_of_Children_from_bSexualb_Offenc_153588598.pdf"
        → "Section_5_in_The_Protection_of_Children_from_Sexual_Offences_153588598.pdf"
    """
    if not name:
        return "document"
    
    # Remove HTML tags (<b>, </b>, <i>, <u>, etc.)
    name = re.sub(r"</?\w+[^>]*>", "", name)
    
    # Remove HTML entities
    name = name.replace("&lt;", "").replace("&gt;", "").replace("&amp;", "&")
    name = name.replace("&quot;", '"').replace("&#39;", "'")
    
    # Remove special characters (keep letters, numbers, spaces, hyphens, underscores)
    name = re.sub(r"[^a-zA-Z0-9 _\-]", "", name)
    
    # Replace multiple spaces with single space
    name = re.sub(r"\s+", " ", name)
    
    # Replace spaces with underscores
    name = name.strip().replace(" ", "_")
    
    # Remove duplicate underscores
    name = re.sub(r"_+", "_", name)
    
    # Remove leading/trailing underscores
    name = name.strip("_")
    
    # Truncate to max length
    return name[:max_len] if name else "document"


def _safe_filename(name: str, max_len: int = 60) -> str:
    """Legacy wrapper - uses _clean_filename for better sanitization."""
    return _clean_filename(name, max_len)
