from sqlalchemy.orm import Session

from app.services.legal_research_service import legal_research_service


class CitationService:
    def find(self, db: Session, proposition: str | dict) -> dict:
        if isinstance(proposition, dict):
            legal_statement = (proposition.get("legal_statement") or "").strip()
            legal_area = (proposition.get("legal_area") or "").strip()
            preferred_court = (proposition.get("preferred_court") or "").strip()
            research_purpose = (proposition.get("research_purpose") or "").strip()
            query = "\n".join(filter(None, [legal_statement, legal_area, preferred_court, research_purpose]))
        else:
            legal_statement, legal_area, preferred_court, research_purpose, query = proposition, "", "", "", proposition
        research = legal_research_service.research(db, query)
        citations = []
        for item in research["relevant_judgments"]:
            court_score = 100 if "supreme court" in (item["court"] or "").lower() else 70
            direct_relevance = item["similarity_score"]
            recent_applicability = 100 if item["year"] and item["year"] >= 2015 else 75
            citation_frequency = 85 if any(word in item["legal_principle"].lower() for word in ("court", "held", "principle")) else 60
            strength = round(court_score * 0.35 + direct_relevance * 0.35 + citation_frequency * 0.15 + recent_applicability * 0.15, 2)
            relationship = "limiting" if any(term in (item["legal_principle"] + " ".join(item["why_this_result"])).lower() for term in ("overruled", "distinguished", "restrictive")) else "supporting"
            citations.append({"citation": item["case_name"], "case_name": item["case_name"], "court": item["court"], "year": item["year"], "bench": item.get("bench"),
                              "relevant_paragraph": item["important_paragraph"]["number"], "paragraph_text": item["important_paragraph"]["text"],
                              "paragraph_explanation": f"This paragraph is the strongest retrieved passage connecting the proposition to the judgment's reasoning.",
                              "legal_principle": item["legal_principle"], "citation_relevance": strength, "authority": "★★★★★" if court_score == 100 else "★★★☆☆",
                              "source_citation": item["source_citation"], "why_this_result": item["why_this_result"], "citation_relationship": relationship,
                              "strength_analysis": {"court_hierarchy": court_score, "direct_relevance": direct_relevance, "citation_frequency": citation_frequency, "recent_applicability": recent_applicability}})
        primary = citations[0] if citations else None
        supporting = [item for item in citations[1:] if item["citation_relationship"] == "supporting"]
        limiting = [item for item in citations if item["citation_relationship"] == "limiting"]
        return {"proposition": legal_statement or query, "legal_principle_extraction": self._extract_principle(query, legal_area, research),
                "primary_authority": primary, "relevant_paragraph": primary, "supporting_citations": supporting,
                "citation_relationship": self._relationships(citations), "limiting_authorities": limiting,
                "citations": citations, "confidence_score": research["confidence_score"], "research_purpose": research_purpose}

    @staticmethod
    def _extract_principle(query: str, legal_area: str, research: dict) -> dict:
        summary = research["research_summary"]
        return {"legal_issue": summary["legal_issue"], "legal_principle": summary["legal_position"],
                "applicable_provisions": summary["applicable_laws"], "legal_area": legal_area or "Indian legal research"}

    @staticmethod
    def _relationships(citations: list[dict]) -> list[dict]:
        return [{"case_name": item["case_name"], "year": item["year"], "relationship": item["citation_relationship"],
                 "description": "Supports the proposition in the retrieved authorities." if item["citation_relationship"] == "supporting" else "May restrict or distinguish the proposition; verify the full judgment."} for item in citations]


citation_service = CitationService()
