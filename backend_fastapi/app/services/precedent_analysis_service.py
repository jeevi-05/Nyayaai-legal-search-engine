"""Precedent retrieval and explainable ranking over the existing repository."""

import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_document import LegalDocument
from app.services.semantic_search_service import semantic_search_service


class PrecedentAnalysisService:
    def analyze(self, db: Session, issue: str, top_k: int = 10) -> dict[str, Any]:
        results = semantic_search_service.search(db, issue, top_k=top_k)
        precedents = []
        for result in results:
            document = db.query(LegalDocument).filter(LegalDocument.id == result["id"]).first()
            if not document:
                continue
            relationship = self.analyze_citation_relationship(document.judgment_text or "", issue)
            precedents.append({
                **result,
                "external_id": document.external_id,
                "binding_strength": self.binding_strength(document, relationship),
                "citation_relationship": relationship,
                "ratio": self.extract_ratio(document),
                "important_observation": (document.court_reasoning or document.summary or "")[:500],
                "relevance_explanation": self.relevance_explanation(document, issue),
                "source_citation": {"case_name": document.case_name or document.title, "paragraph_number": 1, "indian_kanoon_id": document.external_id, "link": document.document_url},
            })
        return {"issue": issue, "precedents": precedents, "citation_graph": self.citation_graph(precedents)}

    def relevance_explanation(self, document, issue: str) -> list[str]:
        reasons = ["Same legal issue"]
        if document.acts_sections and any(token.lower() in document.acts_sections.lower() for token in re.findall(r"Article\s+\d+|Section\s+\d+", issue, re.I)):
            reasons.append("Same statutory provision")
        if "supreme court" in (document.court or "").lower(): reasons.append("Supreme Court authority")
        if "overruled" in (document.judgment_text or "").lower(): reasons.append("Warning: may no longer represent current law")
        return reasons

    @staticmethod
    def binding_strength(document, relationship: str) -> str:
        text = (document.judgment_text or "").lower()
        if "overruled" in text:
            return "Overruled precedent"
        if relationship == "distinguished":
            return "Distinguished precedent"
        if "supreme court" in (document.court or "").lower():
            return "Binding precedent"
        return "Persuasive precedent"

    @staticmethod
    def analyze_citation_relationship(text: str, issue: str) -> str:
        lower = text.lower()
        if "overruled" in lower:
            return "overruled"
        if "distinguish" in lower:
            return "distinguished"
        if re.search(r"\b(relied|followed|approved|cited)\b", lower):
            return "cited"
        return "related"

    @staticmethod
    def extract_ratio(document) -> str:
        return (document.court_reasoning or document.final_decision or document.summary or "No ratio available.")[:900]

    @staticmethod
    def citation_graph(precedents: list[dict]) -> dict[str, list[dict]]:
        nodes = [{"id": p.get("external_id") or str(p["id"]), "label": p["title"]} for p in precedents]
        edges = []
        for p in precedents:
            source = p.get("external_id") or str(p["id"])
            for other in precedents:
                if other is not p:
                    edges.append({"source": source, "target": other.get("external_id") or str(other["id"]), "label": p["citation_relationship"]})
        return {"nodes": nodes, "edges": edges[:30]}


precedent_analysis_service = PrecedentAnalysisService()
