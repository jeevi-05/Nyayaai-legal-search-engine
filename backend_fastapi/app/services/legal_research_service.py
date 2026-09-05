"""Advocate-facing research built exclusively from Indian Kanoon and repository judgments."""

import re
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_document import LegalDocument
from app.services.ik_ingestion_service import ingest_ik_result
from app.services.indian_kanoon_service import search_judgments
from app.services.precedent_analysis_service import precedent_analysis_service
from app.services.semantic_search_service import semantic_search_service


class LegalResearchService:
    def research(self, db: Session, query: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        filters = filters or {}
        # Always query the source first, then ingest results so subsequent vector retrieval has full metadata.
        for item in search_judgments(query):
            try:
                ingest_ik_result(db, item)
            except Exception:
                db.rollback()

        extracted = self.extract_query_metadata(query)
        candidates = semantic_search_service.search(db, query, top_k=30)
        candidates = self._apply_filters(db, candidates, filters)
        authorities = []
        for candidate in candidates[:10]:
            doc = db.get(LegalDocument, candidate["id"])
            if not doc:
                continue
            paragraph = self._important_paragraph(doc, query)
            reasons = precedent_analysis_service.relevance_explanation(doc, query)
            principle = self._legal_principle(doc, paragraph)
            authorities.append({
                "id": doc.external_id or str(doc.id), "case_name": doc.case_name or doc.title,
                "court": doc.court, "year": doc.year, "citation": doc.citation,
                "similarity_score": candidate["similarity"], "important_paragraph": paragraph,
                "legal_principle": principle, "why_relevant": self._why_relevant(reasons, query),
                "source_citation": self._source(doc, paragraph["number"]), "why_this_result": reasons,
            })

        supporting = [item for item in authorities if not self._is_opposing(item)]
        opposing = [item for item in authorities if self._is_opposing(item)]

        return {
            "research_summary": {
                "legal_issue": extracted["legal_issue"],
                "legal_position": self._legal_position(authorities),
                "applicable_laws": extracted["acts_sections"],
                "related_concepts": extracted["concepts"],
            },
            "relevant_judgments": authorities,
            "supporting_authorities": [self._supporting_authority(item) for item in supporting[:5]],
            "opposing_authorities": [self._opposing_authority(item) for item in opposing[:5]],
            "recommended_citations": [self._recommended_citation(item) for item in supporting[:3]],
            "possible_legal_arguments": self._arguments(authorities),
            "confidence_score": self._confidence(authorities),
            "source_count": len(authorities),
        }

    @staticmethod
    def extract_query_metadata(query: str) -> dict[str, Any]:
        acts_sections = re.findall(r"(?:Article|Section)\s+\d+[A-Za-z]*(?:\s+of\s+[\w\s]+)?|\b(?:IPC|CrPC|CPC|NDPS|POCSO)\b", query, re.I)
        concepts = [p.strip() for p in re.split(r"\s*(?:,| and | for | under )\s*", query, flags=re.I) if len(p.strip()) > 3]
        return {"legal_issue": query.strip(), "acts_sections": list(dict.fromkeys(acts_sections)), "concepts": concepts[:8]}

    def _apply_filters(self, db: Session, candidates: list[dict], filters: dict) -> list[dict]:
        min_year, max_year = self._year_bounds(filters)
        output = []
        for item in candidates:
            doc = db.get(LegalDocument, item["id"])
            if not doc:
                continue
            if filters.get("court") and filters["court"].lower() not in (doc.court or "").lower():
                continue
            if filters.get("legal_category") and not self._matches_category(doc, filters["legal_category"]):
                continue
            if min_year and (not doc.year or doc.year < int(min_year)):
                continue
            if max_year and (not doc.year or doc.year > int(max_year)):
                continue
            act_section = f"{doc.acts_sections or ''} {doc.acts or ''}"
            if filters.get("act") and filters["act"].lower() not in act_section.lower():
                continue
            if filters.get("section") and filters["section"].lower() not in act_section.lower():
                continue
            output.append(item)
        return output

    @staticmethod
    def _year_bounds(filters: dict) -> tuple[int | None, int | None]:
        ranges = {"Before 2000": (None, 1999), "2000-2010": (2000, 2010),
                  "2010-2020": (2010, 2020), "2020-Present": (2020, None)}
        selected = filters.get("year")
        if selected in ranges:
            return ranges[selected]
        return filters.get("year_from"), filters.get("year_to")

    @classmethod
    def _matches_category(cls, doc: LegalDocument, category: str) -> bool:
        tokens = {"Criminal Law": ("criminal", "ipc", "crpc", "ndps", "pocso"),
                  "Civil Law": ("civil", "cpc"), "Constitutional Law": ("constitution", "article"),
                  "Family Law": ("family", "marriage", "divorce"), "Property Law": ("property",)}
        text = cls._document_text(doc).lower()
        return any(token in text for token in tokens.get(category, (category.lower(),)))

    @staticmethod
    def _document_text(doc: LegalDocument) -> str:
        return " ".join(filter(None, [doc.acts_sections, doc.acts, doc.sections, doc.tags, doc.summary, doc.legal_issues if hasattr(doc, "legal_issues") else None]))

    @staticmethod
    def _legal_principle(doc: LegalDocument, paragraph: dict[str, Any]) -> str:
        text = doc.court_reasoning or doc.final_decision or doc.summary or paragraph["text"]
        return text[:500] or "No legal principle was extracted from this judgment."

    @staticmethod
    def _why_relevant(reasons: list[str], query: str) -> str:
        return f"Matches the query on {', '.join(reasons).lower()} and provides a cited passage for: {query.strip()}."

    @staticmethod
    def _is_opposing(item: dict[str, Any]) -> bool:
        text = f"{item['legal_principle']} {' '.join(item['why_this_result'])}".lower()
        return any(term in text for term in ("overruled", "distinguished", "restrictive", "dismissed"))

    @staticmethod
    def _supporting_authority(item: dict[str, Any]) -> dict[str, Any]:
        return {"case_name": item["case_name"], "court": item["court"], "year": item["year"],
                "relevance_score": item["similarity_score"], "legal_principle": item["legal_principle"],
                "important_paragraph": item["important_paragraph"], "source_citation": item["source_citation"]}

    @staticmethod
    def _opposing_authority(item: dict[str, Any]) -> dict[str, Any]:
        return {"case_name": item["case_name"], "court": item["court"], "year": item["year"],
                "different_legal_position": item["legal_principle"],
                "reason_for_difference": "The judgment is flagged as restrictive, distinguished, or otherwise different in the retrieved text.",
                "source_citation": item["source_citation"]}

    @staticmethod
    def _recommended_citation(item: dict[str, Any]) -> dict[str, Any]:
        strength = "Strong" if "supreme court" in (item["court"] or "").lower() else "Persuasive"
        return {"case_name": item["case_name"], "court": item["court"], "year": item["year"],
                "citation_strength": strength, "reason": f"{strength} authority with {item['similarity_score']}% query relevance.",
                "legal_principle": item["legal_principle"], "source_citation": item["source_citation"]}

    @staticmethod
    def _important_paragraph(doc: LegalDocument, query: str) -> dict[str, Any]:
        text = doc.court_reasoning or doc.legal_issues or doc.summary or doc.judgment_text or ""
        terms = set(re.findall(r"[a-zA-Z]{4,}", query.lower()))
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\d+[.)])", text) if p.strip()]
        best = max(paragraphs, key=lambda p: sum(t in p.lower() for t in terms), default=text)
        match = re.match(r"\s*(\d+)[.)]", best)
        return {"number": int(match.group(1)) if match else 1, "text": best[:1000] or "No extracted paragraph is available."}

    @staticmethod
    def _source(doc: LegalDocument, paragraph_number: int) -> dict[str, Any]:
        return {"case_name": doc.case_name or doc.title, "court": doc.court, "year": doc.year,
                "paragraph_number": paragraph_number, "indian_kanoon_id": doc.external_id, "link": doc.document_url}

    @staticmethod
    def _legal_position(authorities: list[dict]) -> str:
        if not authorities:
            return "No sufficiently relevant authority was retrieved from the configured legal sources. Refine the issue or filters."
        return "The retrieved authorities address the issue; review the cited paragraphs and the full judgments before relying on a proposition."

    @staticmethod
    def _arguments(authorities: list[dict]) -> list[dict]:
        return [{"point": f"Rely on {a['case_name']} for the overlapping legal issue.", "source_citation": a["source_citation"]} for a in authorities[:5]]

    @staticmethod
    def _confidence(authorities: list[dict]) -> float:
        return round(sum(a["similarity_score"] for a in authorities[:5]) / max(1, min(5, len(authorities))), 2)


legal_research_service = LegalResearchService()
