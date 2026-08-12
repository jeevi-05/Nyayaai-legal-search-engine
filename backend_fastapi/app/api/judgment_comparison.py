"""
Judgment Comparison API
=======================
API endpoints for judgment comparison functionality.
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.services.judgment_comparison_service import judgment_comparison_service
from app.services.semantic_search_service import semantic_search_service

router = APIRouter(
    prefix="/judgments",
    tags=["Judgment Comparison"]
)

logger = logging.getLogger(__name__)


@router.get("/semantic-search")
def semantic_search_judgments(
    query: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    top_k: int = 10
):
    """
    Semantically search for judgments using embeddings.
    
    This endpoint reuses the existing semantic search service
    to find judgments similar to the query.
    """
    try:
        results = semantic_search_service.search(db, query, top_k=top_k)
        
        # Format results for comparison
        formatted_results = []
        for result in results:
            formatted_results.append({
                "judgment_id": result.get("id"),
                "case_title": result.get("title"),
                "court": result.get("court"),
                "year": result.get("year"),
                "citation": result.get("citation"),
                "similarity_score": result.get("similarity", 0),
                "match_reason": result.get("match_reason", "")
            })
        
        return {
            "success": True,
            "query": query,
            "results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again."
        )


@router.post("/compare")
def compare_judgments(
    request: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Compare two judgments using semantic embeddings.
    
    Request body:
    {
        "mode": "judicial",  // Required - must be 'judicial'
        "judgment_a_id": "external_id_of_judgment_a",
        "judgment_b_id": "external_id_of_judgment_b"
    }
    
    Response:
    {
        "judgment_a": {...},
        "judgment_b": {...},
        "overall_similarity": 78.5,
        "comparison": {...},
        "semantic_matches": [...]
    }
    """
    mode = request.get("mode", "")
    judgment_a_id = request.get("judgment_a_id")
    judgment_b_id = request.get("judgment_b_id")
    
    # Validate mode - only Judicial Intelligence Mode allowed
    if mode and mode.lower() != "judicial":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Judgment Comparison is restricted to Judicial Intelligence Mode."
        )
    
    if not judgment_a_id or not judgment_b_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both judgment_a_id and judgment_b_id are required."
        )
    
    if judgment_a_id == judgment_b_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot compare a judgment with itself."
        )
    
    try:
        result = judgment_comparison_service.compare_judgments(
            db, judgment_a_id, judgment_b_id
        )
        
        if "error" in result:
            if result.get("error") == "One or both judgments not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or both judgments not found."
                )
            elif result.get("error") == "Judgment text not available for comparison":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Judgment text not available for comparison."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.get("error", "Comparison failed.")
                )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Judgment comparison failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comparison failed. Please try again."
        )


@router.get("/{judgment_id}/chunks")
def get_judgment_chunks(
    judgment_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get chunks for a judgment (for debugging/preview).
    """
    from app.services.judgment_comparison_service import JudgmentChunker
    
    judgment = db.query(
        type('LegalDocument', (), {'external_id': judgment_id})
    ).filter(
        type('LegalDocument', (), {'external_id': judgment_id})
    ).first()
    
    # Get judgment from repository
    from app.repositories import document_repository
    judgment = document_repository.get_by_external_id(db, judgment_id)
    
    if not judgment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Judgment not found."
        )
    
    text = judgment.judgment_text or ""
    
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Judgment text not available."
        )
    
    chunker = JudgmentChunker()
    chunks = chunker.chunk_text(text, judgment_id)
    
    return {
        "success": True,
        "judgment_id": judgment_id,
        "chunk_count": len(chunks),
        "chunks": chunks
    }
