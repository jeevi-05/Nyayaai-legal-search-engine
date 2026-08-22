"""Topic-level legal synthesis from related repository judgments."""

import re
from sqlalchemy.orm import Session

from app.models.legal_document import LegalDocument
from app.services.semantic_search_service import semantic_search_service
from app.services.precedent_analysis_service import precedent_analysis_service


class CaseLawSynthesisService:
    def synthesize(self, db: Session, topic: str, top_k: int = 12) -> dict:
        matches = semantic_search_service.search(db, topic, top_k=top_k)
        cases = []
        principle_sources = []
        for match in matches:
            doc = db.query(LegalDocument).filter(LegalDocument.id == match["id"]).first()
            if not doc:
                continue
            contribution = (doc.court_reasoning or doc.final_decision or doc.summary or doc.description or "")[:500]
            cases.append({"id": doc.external_id or str(doc.id), "title": doc.title, "court": doc.court, "year": doc.year, "citation": doc.citation, "relevance_score": match["similarity"], "contribution": contribution, "source_citation": {"case_name": doc.case_name or doc.title, "paragraph_number": 1, "indian_kanoon_id": doc.external_id, "link": doc.document_url}})
            principle_sources.append(contribution)
        cases.sort(key=lambda c: (c["year"] or 0, c["title"]))
        principles = self.extract_principles(principle_sources)
        conflicts = self.detect_conflicts(principle_sources)
        return {
            "topic": topic,
            "timeline": [{"year": case["year"], "case": case["title"], "event": case["contribution"]} for case in cases],
            "major_cases": cases,
            "common_legal_principles": principles,
            "conflicting_views": conflicts,
            "current_legal_position": self.generate_legal_summary(topic, cases, principles, conflicts),
            "confidence_score": 0.78 if cases else 0.2,
        }

    @staticmethod
    def extract_principles(texts: list[str]) -> list[str]:
        sentences = []
        for text in texts:
            sentences.extend(re.split(r"(?<=[.!?])\s+", text))
        candidates = [s.strip() for s in sentences if len(s.strip()) > 45 and re.search(r"\b(right|principle|held|must|shall|article|section|law)\b", s, re.I)]
        return list(dict.fromkeys(candidates))[:6] or ["No repeated principle could be extracted from the available judgments."]

    @staticmethod
    def detect_conflicts(texts: list[str]) -> list[str]:
        conflicts = [text[:500] for text in texts if re.search(r"\b(however|but|distinguish|not applicable|overruled|contrary)\b", text, re.I)]
        return conflicts[:5] or ["No explicit conflicting judicial view was identified in the retrieved material."]

    @staticmethod
    def generate_legal_summary(topic: str, cases: list[dict], principles: list[str], conflicts: list[str]) -> str:
        if not cases:
            return f"No repository judgments with usable embeddings were found for '{topic}'."
        latest = cases[-1]
        return f"For {topic}, the retrieved case law contains {len(cases)} relevant decisions. The latest retrieved decision is {latest['title']} ({latest['year'] or 'year unavailable'}). The current position should be read from the repeated principles and any identified distinctions; this synthesis is research assistance, not a substitute for reviewing the full judgments."


case_law_synthesis_service = CaseLawSynthesisService()
