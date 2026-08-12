"""
Indian Kanoon API Service
All document endpoints require POST (not GET).
Docs: https://api.indiankanoon.org/api/
"""

import re
import httpx
from loguru import logger
from app.core.config import get_settings

settings = get_settings()

_BASE_URL    = "https://api.indiankanoon.org"
_TIMEOUT_DOC = 20
_TIMEOUT_PDF = 30


def _headers() -> dict:
    return {
        "Authorization": f"Token {settings.INDIAN_KANOON_API_TOKEN}",
        "Accept": "application/json",
    }


# ── Search ────────────────────────────────────────────────────────────────────

def search_judgments(query: str, page_num: int = 0) -> list[dict]:
    """POST /search/ — returns list of result dicts."""
    if not settings.INDIAN_KANOON_API_TOKEN:
        logger.warning("INDIAN_KANOON_API_TOKEN not set — skipping IK search")
        return []
    try:
        with httpx.Client(timeout=_TIMEOUT_DOC) as client:
            resp = client.post(
                f"{_BASE_URL}/search/",
                headers=_headers(),
                data={"formInput": query, "pagenum": page_num},
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for doc in data.get("docs", []):
            doc_id = str(doc.get("tid", ""))
            results.append({
                "title":        doc.get("title", "Untitled"),
                "court":        doc.get("docsource", ""),
                "year":         _extract_year(doc.get("publishdate", "")),
                "citation":     doc.get("citation", ""),
                "document_url": f"https://indiankanoon.org/doc/{doc_id}/",
                "snippet":      _strip_html(doc.get("headline", "")),
                "doc_id":       doc_id,
            })
        logger.info("IK search: {} results for '{}'", len(results), query)
        return results

    except httpx.HTTPStatusError as e:
        logger.error("IK search HTTP {}: {}", e.response.status_code, e.response.text[:200])
        return []
    except Exception as e:
        logger.error("IK search failed: {}", e)
        return []


# ── Document detail ───────────────────────────────────────────────────────────

def fetch_document_metadata(doc_id: str) -> dict | None:
    """
    POST /doc/{id}/ — fetch full judgment.
    Returns normalised dict or None on failure.
    """
    if not settings.INDIAN_KANOON_API_TOKEN:
        logger.warning("INDIAN_KANOON_API_TOKEN not set")
        return None

    try:
        with httpx.Client(timeout=_TIMEOUT_DOC) as client:
            resp = client.post(
                f"{_BASE_URL}/doc/{doc_id}/",
                headers=_headers(),
            )
            resp.raise_for_status()
            data = resp.json()

        raw_html      = data.get("doc", "")
        judgment_text = _clean_judgment_html(raw_html)

        # Tags / categories from IK
        cats = data.get("cats", [])
        tags = ", ".join(c.get("value", "") for c in cats if c.get("value")) if isinstance(cats, list) else ""

        return {
            "doc_id":        doc_id,
            "title":         data.get("title", "Untitled"),
            "court":         data.get("docsource", ""),
            "date":          data.get("publishdate", ""),
            "year":          _extract_year(data.get("publishdate", "")),
            "citation":      "",           # IK search result has citation; doc endpoint may not
            "judges":        _extract_bench_from_text(judgment_text),
            "author":        _extract_author_from_text(judgment_text),
            "judgment_text": judgment_text,
            "tags":          tags,
            "document_url":  f"https://indiankanoon.org/doc/{doc_id}/",
            "snippet":       judgment_text[:400] if judgment_text else "",
        }

    except httpx.HTTPStatusError as e:
        logger.error("IK doc/{} HTTP {}: {}", doc_id, e.response.status_code, e.response.text[:200])
        return None
    except Exception as e:
        logger.error("IK fetch_document_metadata doc_id={}: {}", doc_id, e)
        return None


def fetch_document_text(doc_id: str) -> str:
    """Convenience wrapper — returns plain judgment text or empty string."""
    meta = fetch_document_metadata(doc_id)
    return meta.get("judgment_text", "") if meta else ""


# ── PDF ───────────────────────────────────────────────────────────────────────

def fetch_document_pdf_bytes(doc_id: str) -> bytes | None:
    """
    Try GET /docpdf/{id}/ — IK provides PDFs for some documents.
    Returns bytes if available, None otherwise.
    """
    if not settings.INDIAN_KANOON_API_TOKEN:
        return None
    try:
        with httpx.Client(timeout=_TIMEOUT_PDF) as client:
            resp = client.get(
                f"{_BASE_URL}/docpdf/{doc_id}/",
                headers=_headers(),
            )
        if resp.status_code == 200:
            ct = resp.headers.get("content-type", "")
            if "pdf" in ct or resp.content[:4] == b"%PDF":
                logger.info("IK PDF available for doc_id={}", doc_id)
                return resp.content
        logger.info("IK PDF not available for doc_id={} (status={})", doc_id, resp.status_code)
        return None
    except Exception as e:
        logger.warning("IK PDF fetch failed doc_id={}: {}", doc_id, e)
        return None


# ── HTML cleaning ─────────────────────────────────────────────────────────────

def _strip_html(html: str) -> str:
    """Remove all HTML tags."""
    return re.sub(r"<[^>]+>", "", html or "").strip()


def _clean_judgment_html(html: str) -> str:
    """
    Convert IK judgment HTML to clean readable plain text.
    Preserves paragraph breaks and removes navigation/header noise.
    """
    if not html:
        return ""

    # Replace block elements with newlines before stripping
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p>|</div>|</li>|</tr>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)

    # Decode common HTML entities
    text = (text
            .replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'"))

    # Collapse excessive blank lines
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    # Collapse excessive spaces
    text = re.sub(r"[ \t]{3,}", "  ", text)

    return text.strip()


# ── Metadata helpers ──────────────────────────────────────────────────────────

def _extract_year(date_str: str) -> int | None:
    if not date_str:
        return None
    for part in re.split(r"[\s\-/]", date_str):
        if len(part) == 4 and part.isdigit():
            return int(part)
    return None


def _extract_bench_from_text(text: str) -> str:
    """Extract bench/judges line from cleaned judgment text."""
    m = re.search(r"Bench\s*:\s*(.+)", text[:2000], re.IGNORECASE)
    if m:
        return m.group(1).strip()[:200]
    m = re.search(r"(?:BEFORE|CORAM)\s*:?\s*(.+)", text[:2000], re.IGNORECASE)
    if m:
        return m.group(1).strip()[:200]
    return ""


def _extract_author_from_text(text: str) -> str:
    """Extract author/judge who wrote the judgment."""
    m = re.search(r"Author\s*:\s*(.+)", text[:2000], re.IGNORECASE)
    if m:
        return m.group(1).strip()[:100]
    return ""
