from sqlalchemy.orm import Session
from app.repositories import document_repository


def get_stats(db: Session) -> dict:
    """Return dashboard statistics. Extend in Phase 2 with search/bookmark counts."""
    return {
        "total_documents": document_repository.count(db),
        "searches": 0,       # Phase 2: track per-user search history
        "bookmarks": 0,      # Phase 2: bookmarks feature
        "reports": 0,        # Phase 2: report generation
    }
