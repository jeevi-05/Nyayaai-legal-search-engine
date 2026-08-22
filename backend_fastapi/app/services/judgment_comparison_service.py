"""
Judgment Comparison Service
===========================
Compares two legal judgments using semantic embeddings and vector similarity.

Core approach:
- Chunk judgments into meaningful sections
- Generate embeddings for each chunk
- Use cosine similarity for semantic alignment
- Extract legal components for structured comparison
- Identify similarities, differences, and potential conflicts
"""

import json
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from sqlalchemy.orm import Session

from app.services.embedding_service import EmbeddingService
from app.services.case_processing_service import process_judgment
from app.repositories import document_repository


class JudgmentChunker:
    """Chunks judgments into meaningful sections for semantic comparison."""
    
    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.embedding_service = EmbeddingService()
    
    def chunk_text(self, text: str, judgment_id: str) -> List[Dict[str, Any]]:
        """
        Chunk judgment text into meaningful sections.
        
        Strategy:
        1. First try to extract explicit sections (Facts, Issues, Arguments, etc.)
        2. Fall back to paragraph-based chunking
        3. Ensure chunks are 300-700 tokens with small overlap
        """
        chunks = []
        
        if not text or len(text.strip()) < 100:
            return chunks
        
        # Try to extract explicit sections first
        sections = self._extract_sections(text)
        
        if sections:
            for section_name, section_text in sections.items():
                if section_text and len(section_text.strip()) > 50:
                    chunk_id = self._generate_chunk_id(judgment_id, section_name)
                    chunk = {
                        "chunk_id": chunk_id,
                        "judgment_id": judgment_id,
                        "section": section_name,
                        "text": section_text.strip(),
                        "chunk_type": "section",
                        "paragraph_index": 0
                    }
                    chunks.append(chunk)
        else:
            # Fall back to paragraph-based chunking
            paragraphs = self._split_into_paragraphs(text)
            
            current_chunk = ""
            para_indices = []
            
            for idx, para in enumerate(paragraphs):
                if len(current_chunk) + len(para) <= self.max_chunk_size:
                    current_chunk += para + "\n\n"
                    para_indices.append(idx)
                else:
                    if current_chunk.strip():
                        chunk_id = self._generate_chunk_id(judgment_id, f"para_{para_indices[0]}_{para_indices[-1]}")
                        chunk = {
                            "chunk_id": chunk_id,
                            "judgment_id": judgment_id,
                            "section": "Body",
                            "text": current_chunk.strip(),
                            "chunk_type": "paragraph",
                            "paragraph_indices": para_indices
                        }
                        chunks.append(chunk)
                    
                    # Start new chunk with overlap
                    current_chunk = para + "\n\n"
                    para_indices = [idx]
            
            # Don't forget the last chunk
            if current_chunk.strip():
                chunk_id = self._generate_chunk_id(judgment_id, f"para_{para_indices[0]}_{para_indices[-1]}")
                chunk = {
                    "chunk_id": chunk_id,
                    "judgment_id": judgment_id,
                    "section": "Body",
                    "text": current_chunk.strip(),
                    "chunk_type": "paragraph",
                    "paragraph_indices": para_indices
                }
                chunks.append(chunk)
        
        return chunks
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract explicit sections from judgment text."""
        sections = {}
        
        section_patterns = {
            "Facts": [
                r"FACTS?\s+OF\s+(THE\s+)?CASE",
                r"STATEMENT\s+OF\s+FACTS?",
                r"BACKGROUND",
                r"BRIEF\s+FACTS?"
            ],
            "Legal Issues": [
                r"ISSUES?\s+(RAISED|INVOLVED|FOR\s+(CONSIDERATION|DETERMINATION))",
                r"QUESTIONS?\s+(OF\s+LAW|BEFORE\s+(THE\s+)?COURT)",
                r"POINTS?\s+(FOR\s+)?DETERMINATION"
            ],
            "Arguments": [
                r"ARGUMENTS?\s+(OF|BY|FOR)\s+(THE\s+)?(?:PARTIES|APPELLANT|PETITIONER|PLAINTIFF|RESPONDENT)",
                r"SUBMISSIONS?\s+(OF|BY|FOR)",
                r"CONTENTIONS?\s+(OF|BY|FOR)"
            ],
            "Court Reasoning": [
                r"COURT'?S?\s+(REASONING|ANALYSIS|OBSERVATIONS?)",
                r"REASONING\s+AND\s+ANALYSIS",
                r"ANALYSIS\s+AND\s+DISCUSSION",
                r"DISCUSSION",
                r"ANALYSIS",
                r"OBSERVATIONS?"
            ],
            "Final Decision": [
                r"(FINAL\s+)?ORDER",
                r"CONCLUSION",
                r"RESULT",
                r"OPERATIVE\s+PART",
                r"DISPOSED?\s+OF"
            ],
            "Statutes": [
                r"APPLICABLE\s+LAW",
                r"STATUTORY\s+PROVISIONS?",
                r"RELEVANT\s+PROVISIONS?"
            ]
        }
        
        for section_name, patterns in section_patterns.items():
            combined = "|".join(f"(?:{p})" for p in patterns)
            full_pat = rf"(?:^|\n)\s*(?:{combined})\s*\n(.*?)(?=\n\s*[A-Z][A-Z\s]{{4,}}\s*\n|\Z)"
            
            match = re.search(full_pat, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
        
        return sections
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split on double newlines
        paragraphs = re.split(r'\n\s*\n', text)
        # Clean up paragraphs
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 20]
        return paragraphs
    
    def _generate_chunk_id(self, judgment_id: str, suffix: str) -> str:
        """Generate unique chunk ID."""
        hash_input = f"{judgment_id}_{suffix}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


class JudgmentComparisonService:
    """Core judgment comparison service using semantic embeddings."""
    
    def __init__(self):
        self.chunker = JudgmentChunker()
        self.embedding_service = EmbeddingService()
    
    def compare_judgments(
        self,
        db: Session,
        judgment_a_id: str,
        judgment_b_id: str
    ) -> Dict[str, Any]:
        """
        Compare two judgments using semantic embeddings.
        
        Returns structured comparison with:
        - Overall similarity score
        - Component-level comparisons
        - Semantic matches with evidence
        """
        # Get judgments from database
        judgment_a = self._get_judgment(db, judgment_a_id)
        judgment_b = self._get_judgment(db, judgment_b_id)
        
        if not judgment_a or not judgment_b:
            return {
                "error": "One or both judgments not found",
                "judgment_a_id": judgment_a_id,
                "judgment_b_id": judgment_b_id
            }
        
        # Extract judgment texts
        text_a = judgment_a.judgment_text or ""
        text_b = judgment_b.judgment_text or ""
        
        if not text_a.strip() or not text_b.strip():
            return {
                "error": "Judgment text not available for comparison",
                "judgment_a_id": judgment_a_id,
                "judgment_b_id": judgment_b_id
            }
        
        # Chunk judgments
        chunks_a = self.chunker.chunk_text(text_a, judgment_a_id)
        chunks_b = self.chunker.chunk_text(text_b, judgment_b_id)
        
        if not chunks_a or not chunks_b:
            return {
                "error": "Could not chunk judgments for comparison",
                "judgment_a_id": judgment_a_id,
                "judgment_b_id": judgment_b_id
            }
        
        # Generate embeddings for chunks
        embeddings_a = self._generate_chunk_embeddings(chunks_a)
        embeddings_b = self._generate_chunk_embeddings(chunks_b)
        
        # Calculate semantic similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(
            embeddings_a, embeddings_b
        )
        
        # Align semantically related chunks
        aligned_chunks = self._align_chunks(
            chunks_a, chunks_b, similarity_matrix, top_k=3
        )
        
        # Extract legal components
        structured_a = self._extract_legal_components(judgment_a)
        structured_b = self._extract_legal_components(judgment_b)
        
        # Generate comparison
        comparison = self._generate_comparison(
            structured_a, structured_b, aligned_chunks
        )
        
        # Calculate overall similarity
        overall_similarity = self._calculate_overall_similarity(
            embeddings_a, embeddings_b
        )

        legal_similarity = self.calculate_legal_similarity(structured_a, structured_b, overall_similarity)
        precedent_treatment = self.compare_precedents(judgment_a, judgment_b)
        
        return {
            "judgment_a": self._format_judgment(judgment_a),
            "judgment_b": self._format_judgment(judgment_b),
            "overall_similarity": round(overall_similarity * 100, 2),
            "legal_similarity": legal_similarity,
            "comparison": comparison,
            "precedent_treatment": precedent_treatment,
            "source_citations": [self._source_citation(judgment_a), self._source_citation(judgment_b)],
            "semantic_matches": aligned_chunks,
            "chunk_count_a": len(chunks_a),
            "chunk_count_b": len(chunks_b)
        }

    def calculate_legal_similarity(self, a: Dict, b: Dict, text_similarity: float) -> Dict[str, float]:
        """Explainable composite score; legal dimensions are not collapsed into text overlap."""
        issue = self._estimate_similarity(a.get("legal_issues", ""), b.get("legal_issues", ""))
        statutes = self._calculate_jaccard_similarity(set(a.get("statutes", [])), set(b.get("statutes", [])))
        precedents = self._calculate_jaccard_similarity(set(a.get("precedents", [])), set(b.get("precedents", [])))
        overall = text_similarity * .35 + issue * .35 + statutes * .20 + precedents * .10
        return {"text_similarity": round(text_similarity * 100, 2), "legal_issue_similarity": round(issue * 100, 2), "statutory_similarity": round(statutes * 100, 2), "precedent_similarity": round(precedents * 100, 2), "overall_legal_similarity": round(overall * 100, 2)}

    def compare_precedents(self, judgment_a, judgment_b) -> Dict[str, Dict[str, List[str]]]:
        def treatment(text: str) -> Dict[str, List[str]]:
            output = {"followed": [], "distinguished": [], "overruled": [], "referred": []}
            for case in self._extract_precedents(text):
                index = text.lower().find(case.lower())
                window = text[max(0, index - 160):index + len(case) + 160].lower()
                label = "followed" if re.search(r"followed|relied upon|approved", window) else "distinguished" if "distinguish" in window else "overruled" if "overruled" in window else "referred"
                output[label].append(case)
            return output
        return {"judgment_a": treatment(judgment_a.judgment_text or ""), "judgment_b": treatment(judgment_b.judgment_text or "")}

    @staticmethod
    def _source_citation(judgment) -> Dict[str, Any]:
        return {"case_name": judgment.case_name or judgment.title, "paragraph_number": 1, "indian_kanoon_id": judgment.external_id, "link": judgment.document_url}
    
    def _generate_chunk_embeddings(self, chunks: List[Dict]) -> List[List[float]]:
        """Generate embeddings for chunks."""
        embeddings = []
        for chunk in chunks:
            embedding = self.embedding_service.embed(chunk["text"])
            if embedding:
                embeddings.append(embedding)
        return embeddings

    @staticmethod
    def _get_judgment(db: Session, judgment_id: str):
        """Accept both Indian Kanoon IDs and locally uploaded/repository integer IDs."""
        judgment = document_repository.get_by_external_id(db, judgment_id)
        if judgment:
            return judgment
        try:
            from app.models.legal_document import LegalDocument
            return db.query(LegalDocument).filter(LegalDocument.id == int(judgment_id)).first()
        except (TypeError, ValueError):
            return None
    
    def _calculate_similarity_matrix(
        self,
        embeddings_a: List[List[float]],
        embeddings_b: List[List[float]]
    ) -> List[List[float]]:
        """Calculate cosine similarity matrix between two sets of embeddings."""
        import numpy as np
        
        matrix = []
        for emb_a in embeddings_a:
            row = []
            for emb_b in embeddings_b:
                sim = self._cosine_similarity(emb_a, emb_b)
                row.append(sim)
            matrix.append(row)
        return matrix
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        
        a = np.array(vec1)
        b = np.array(vec2)
        
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _align_chunks(
        self,
        chunks_a: List[Dict],
        chunks_b: List[Dict],
        similarity_matrix: List[List[float]],
        top_k: int = 3
    ) -> List[Dict]:
        """Align semantically related chunks between two judgments."""
        aligned = []
        
        for i, chunk_a in enumerate(chunks_a):
            # Get top-k most similar chunks from judgment B
            similarities = similarity_matrix[i]
            top_indices = sorted(
                range(len(similarities)),
                key=lambda x: similarities[x],
                reverse=True
            )[:top_k]
            
            for j in top_indices:
                if similarities[j] >= 0.55:  # Minimum similarity threshold
                    aligned.append({
                        "chunk_a": chunk_a,
                        "chunk_b": chunks_b[j],
                        "similarity": round(similarities[j] * 100, 2),
                        "threshold_passed": similarities[j] >= 0.70
                    })
        
        # Sort by similarity
        aligned.sort(key=lambda x: x["similarity"], reverse=True)
        
        return aligned[:20]  # Limit to top 20 matches
    
    def _extract_legal_components(self, judgment) -> Dict[str, Any]:
        """Extract structured legal components from judgment."""
        text = judgment.judgment_text or ""
        
        processed = process_judgment(text)
        
        # Extract statutes
        statutes = []
        if processed.get("acts_sections"):
            statutes = [s.strip() for s in processed["acts_sections"].split(",") if s.strip()]
        
        # Extract precedents (cases mentioned)
        precedents = self._extract_precedents(text)
        
        return {
            "facts": processed.get("case_facts", ""),
            "legal_issues": processed.get("legal_issues", ""),
            "arguments": processed.get("arguments", ""),
            "statutes": statutes,
            "precedents": precedents,
            "reasoning": processed.get("court_reasoning", ""),
            "decision": processed.get("final_decision", ""),
            "judges": judgment.judges or "",
            "court": judgment.court or "",
            "year": judgment.year or ""
        }
    
    def _extract_precedents(self, text: str) -> List[str]:
        """Extract case names/precedents from judgment text."""
        # Pattern for case names
        patterns = [
            r"([A-Z][a-zA-Z\s]+?\s+v\s+[A-Z][a-zA-Z\s]+?)\s*,?\s*\d{4}",
            r"(In\s+Re\s+[A-Z][a-zA-Z\s]+?)\s*,?\s*\d{4}",
            r"([A-Z][a-zA-Z\s]+?\s+vs\s+[A-Z][a-zA-Z\s]+?)\s*,?\s*\d{4}",
        ]
        
        precedents = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                precedents.add(match.strip())
        
        return list(precedents)[:20]  # Limit to top 20
    
    def _generate_comparison(
        self,
        structured_a: Dict,
        structured_b: Dict,
        aligned_chunks: List[Dict]
    ) -> Dict[str, Any]:
        """Generate structured comparison from aligned chunks."""
        return {
            "facts": self._compare_facts(structured_a, structured_b),
            "legal_issues": self._compare_issues(structured_a, structured_b),
            "arguments": self._compare_arguments(structured_a, structured_b),
            "statutes": self._compare_statutes(structured_a, structured_b),
            "precedents": self._compare_precedents(structured_a, structured_b),
            "reasoning": self._compare_reasoning(structured_a, structured_b),
            "outcome": self._compare_outcome(structured_a, structured_b)
        }
    
    def _compare_facts(self, a: Dict, b: Dict) -> Dict[str, Any]:
        """Compare facts between judgments."""
        return {
            "judgment_a": a.get("facts", "")[:500],
            "judgment_b": b.get("facts", "")[:500],
            "similarity_score": self._estimate_similarity(a.get("facts", ""), b.get("facts", "")),
            "common_elements": self._find_common_elements(a.get("facts", ""), b.get("facts", "")),
            "key_differences": self._find_differences(a.get("facts", ""), b.get("facts", ""))
        }
    
    def _compare_issues(self, a: Dict, b: Dict) -> Dict[str, Any]:
        """Compare legal issues between judgments."""
        return {
            "judgment_a": a.get("legal_issues", "")[:500],
            "judgment_b": b.get("legal_issues", "")[:500],
            "similarity_score": self._estimate_similarity(a.get("legal_issues", ""), b.get("legal_issues", "")),
            "common_issues": self._find_common_elements(a.get("legal_issues", ""), b.get("legal_issues", "")),
            "unique_issues_a": self._find_unique_elements(a.get("legal_issues", ""), b.get("legal_issues", "")),
            "unique_issues_b": self._find_unique_elements(b.get("legal_issues", ""), a.get("legal_issues", ""))
        }
    
    def _compare_arguments(self, a: Dict, b: Dict) -> Dict[str, Any]:
        """Compare arguments between judgments."""
        return {
            "judgment_a": a.get("arguments", "")[:500],
            "judgment_b": b.get("arguments", "")[:500],
            "similarity_score": self._estimate_similarity(a.get("arguments", ""), b.get("arguments", ""))
        }
    
    def _compare_statutes(self, a: Dict, b: Dict) -> Dict[str, Any]:
        """Compare statutes between judgments."""
        statutes_a = set(a.get("statutes", []))
        statutes_b = set(b.get("statutes", []))
        
        common = statutes_a & statutes_b
        only_a = statutes_a - statutes_b
        only_b = statutes_b - statutes_a
        
        return {
            "common_statutes": list(common)[:10],
            "only_in_judgment_a": list(only_a)[:10],
            "only_in_judgment_b": list(only_b)[:10],
            "similarity_score": self._calculate_jaccard_similarity(statutes_a, statutes_b)
        }
    
    def _compare_precedents(self, a: Dict, b: Dict) -> Dict[str, Any]:
        """Compare precedents between judgments."""
        precedents_a = set(a.get("precedents", []))
        precedents_b = set(b.get("precedents", []))
        
        common = precedents_a & precedents_b
        only_a = precedents_a - precedents_b
        only_b = precedents_b - precedents_a
        
        return {
            "common_precedents": list(common)[:10],
            "only_in_judgment_a": list(only_a)[:10],
            "only_in_judgment_b": list(only_b)[:10],
            "similarity_score": self._calculate_jaccard_similarity(precedents_a, precedents_b)
        }
    
    def _compare_reasoning(self, a: Dict, b: Dict) -> Dict[str, Any]:
        """Compare legal reasoning between judgments."""
        reasoning_a = a.get("reasoning", "")
        reasoning_b = b.get("reasoning", "")
        
        return {
            "judgment_a": reasoning_a[:500],
            "judgment_b": reasoning_b[:500],
            "similarity_score": self._estimate_similarity(reasoning_a, reasoning_b),
            "relationship": self._determine_reasoning_relationship(reasoning_a, reasoning_b)
        }
    
    def _compare_outcome(self, a: Dict, b: Dict) -> Dict[str, Any]:
        """Compare final outcomes between judgments."""
        return {
            "judgment_a": a.get("decision", "")[:300],
            "judgment_b": b.get("decision", "")[:300],
            "similarity_score": self._estimate_similarity(a.get("decision", ""), b.get("decision", ""))
        }
    
    def _estimate_similarity(self, text_a: str, text_b: str) -> float:
        """Estimate text similarity using simple heuristics."""
        if not text_a or not text_b:
            return 0.0
        
        # Simple word overlap as heuristic
        words_a = set(re.findall(r'\b\w+\b', text_a.lower()))
        words_b = set(re.findall(r'\b\w+\b', text_b.lower()))
        
        if not words_a or not words_b:
            return 0.0
        
        intersection = words_a & words_b
        union = words_a | words_b
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_jaccard_similarity(self, set_a, set_b) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set_a or not set_b:
            return 0.0
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        return intersection / union if union else 0.0
    
    def _find_common_elements(self, text_a: str, text_b: str) -> List[str]:
        """Find common elements between two texts."""
        words_a = set(re.findall(r'\b\w+\b', text_a.lower()))
        words_b = set(re.findall(r'\b\w+\b', text_b.lower()))
        
        common = words_a & words_b
        return list(common)[:10]
    
    def _find_differences(self, text_a: str, text_b: str) -> List[str]:
        """Find key differences between two texts."""
        words_a = set(re.findall(r'\b\w+\b', text_a.lower()))
        words_b = set(re.findall(r'\b\w+\b', text_b.lower()))
        
        diff_a = words_a - words_b
        diff_b = words_b - words_a
        
        return {
            "unique_to_judgment_a": list(diff_a)[:5],
            "unique_to_judgment_b": list(diff_b)[:5]
        }
    
    def _find_unique_elements(self, text_a: str, text_b: str) -> List[str]:
        """Find elements unique to text_a."""
        words_a = set(re.findall(r'\b\w+\b', text_a.lower()))
        words_b = set(re.findall(r'\b\w+\b', text_b.lower()))
        
        return list(words_a - words_b)[:10]
    
    def _determine_reasoning_relationship(self, reasoning_a: str, reasoning_b: str) -> str:
        """Determine the relationship between two reasoning passages."""
        if not reasoning_a or not reasoning_b:
            return "Insufficient evidence"
        
        # Simple heuristic-based determination
        similarity = self._estimate_similarity(reasoning_a, reasoning_b)
        
        if similarity >= 0.70:
            return "Similar reasoning approach"
        elif similarity >= 0.50:
            return "Related but different approach"
        else:
            return "Potentially different/conflicting approach"
    
    def _calculate_overall_similarity(
        self,
        embeddings_a: List[List[float]],
        embeddings_b: List[List[float]]
    ) -> float:
        """Calculate overall semantic similarity between two judgments."""
        if not embeddings_a or not embeddings_b:
            return 0.0
        
        import numpy as np
        
        # Average of all pairwise similarities
        total_sim = 0.0
        count = 0
        
        for emb_a in embeddings_a:
            for emb_b in embeddings_b:
                sim = self._cosine_similarity(emb_a, emb_b)
                total_sim += sim
                count += 1
        
        return total_sim / count if count > 0 else 0.0
    
    def _format_judgment(self, judgment) -> Dict[str, Any]:
        """Format judgment for API response."""
        return {
            "judgment_id": judgment.external_id,
            "case_title": judgment.title,
            "court": judgment.court,
            "year": judgment.year,
            "citation": judgment.citation,
            "bench": judgment.judges,
            "source": judgment.source or "Indian Kanoon"
        }


# Global instance
judgment_comparison_service = JudgmentComparisonService()
