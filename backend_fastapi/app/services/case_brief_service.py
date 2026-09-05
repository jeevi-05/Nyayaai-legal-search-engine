import html
import re
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_document import LegalDocument
from app.services.case_processing_service import process_judgment
from app.services.legal_research_service import legal_research_service
from app.services.semantic_search_service import semantic_search_service


class CaseBriefService:
    INSUFFICIENT = "Insufficient source data to determine this."

    def compare(self, db: Session, payload: dict[str, Any]) -> dict[str, Any]:
        facts = self._clean(payload.get("case_facts"))
        issue = self._clean(payload.get("legal_issue"))
        if not facts or not issue:
            raise ValueError("Case facts and legal issue are required.")
        law = self._clean(payload.get("relevant_law"))
        case_type = self._clean(payload.get("case_type"))
        preferred_court = self._clean(payload.get("preferred_court"))
        start_year = self._year(payload.get("start_year"))
        end_year = self._year(payload.get("end_year"))
        extracted = self._extract_input(facts, issue, law)
        query = "\n".join(filter(None, [issue, facts, law, extracted["procedural_stage"]]))

        from app.services.indian_kanoon_service import search_judgments
        for item in search_judgments(query):
            try:
                from app.services.ik_ingestion_service import ingest_ik_result
                ingest_ik_result(db, item)
            except Exception:
                db.rollback()

        candidates = semantic_search_service.search(db, query, top_k=30)
        cases = []
        query_terms = self._terms(" ".join([facts, issue, law]))
        for candidate in candidates:
            doc = db.get(LegalDocument, candidate["id"])
            if not doc or not self._within_years(doc.year, start_year, end_year):
                continue
            if preferred_court and preferred_court != "All Courts" and preferred_court.lower() not in (doc.court or "").lower():
                continue
            score = self._score(doc, candidate["similarity"], query_terms, law, case_type)
            cases.append(self._case_result(doc, score, facts, issue, law))
        cases.sort(key=lambda item: item["similarity_score"], reverse=True)
        cases = cases[:10]
        favorable = sum(item["favorability"] == "Favorable" for item in cases)
        unfavorable = sum(item["favorability"] == "Unfavorable" for item in cases)
        return {"case_understanding": extracted, "legal_issue_identified": issue,
                "relevant_laws": extracted["relevant_statutes"], "similar_cases": cases,
                "overall_research_insight": self._insight(cases, favorable, unfavorable),
                "research_note": "Research analysis only. It is not a prediction of the outcome in the current case."}

    def _case_result(self, doc: LegalDocument, score: float, facts: str, issue: str, law: str) -> dict[str, Any]:
        text = self._clean(doc.judgment_text or doc.extracted_text or "")
        reasoning = self._clean(doc.court_reasoning or "") or self._extract_sentences(text, r"reason|therefore|held|conclude")
        outcome = self._outcome(doc.final_decision or text)
        paragraph = self._paragraph(text, issue, law)
        similar, different = self._fact_comparison(facts, self._clean(doc.case_facts or ""))
        favorability = self._favorability(outcome, facts)
        source = legal_research_service._source(doc, paragraph["number"])
        return {"case_name": doc.case_name or doc.title, "court": doc.court or self.INSUFFICIENT, "year": doc.year,
                "judges": doc.judges, "citation": doc.citation, "indian_kanoon_id": doc.external_id,
                "similarity_score": score, "similarity_explanation": self._similarity_explanation(score),
                "outcome": outcome, "court_reasoning": reasoning or self.INSUFFICIENT,
                "relevant_paragraphs": [paragraph] if paragraph["text"] else [], "similar_facts": similar,
                "distinguishing_facts": different, "favorability": favorability,
                "favorability_reason": self._favorability_reason(favorability, outcome), "source_citation": source}

    @classmethod
    def _extract_input(cls, facts: str, issue: str, law: str) -> dict[str, Any]:
        stage = cls._extract_phrase(facts, r"(?:at the stage of|during|after|before)\s+([^.;,]+)")
        relief = cls._extract_phrase(facts, r"(?:seeking|seeks|prays for|relief sought)\s+([^.;]+)")
        roles = re.findall(r"\b(accused|appellant|respondent|petitioner|plaintiff|defendant|complainant|prosecution)\b", facts, re.I)
        statutes = list(dict.fromkeys(re.findall(r"(?:Section|Article)\s+\d+[A-Za-z]*(?:\s+of\s+[A-Za-z][\w\s,]+)?|\b(?:IPC|CrPC|CPC|NDPS|POCSO)\b", f"{facts} {issue} {law}", re.I)))
        return {"parties_or_roles": list(dict.fromkeys(role.lower() for role in roles)), "material_facts": facts,
                "procedural_stage": stage or cls.INSUFFICIENT, "legal_issue": issue, "relevant_statutes": statutes,
                "important_factual_circumstances": sorted(cls._terms(facts))[:12], "relief_sought": relief or cls.INSUFFICIENT,
                "positions": cls.INSUFFICIENT}

    @staticmethod
    def _score(doc: LegalDocument, semantic: float, terms: set[str], law: str, case_type: str) -> float:
        text = " ".join(filter(None, [doc.case_facts, doc.legal_issues, doc.acts_sections, doc.court_reasoning, doc.summary])).lower()
        overlap = len(terms & set(re.findall(r"[a-z]{4,}", text))) / max(1, len(terms)) * 100
        statutory = 100 if law and any(part.lower() in text for part in re.findall(r"[\w]+", law) if len(part) > 3) else (50 if not law else 0)
        authority = 100 if "supreme court" in (doc.court or "").lower() else 75 if "high court" in (doc.court or "").lower() else 50
        type_match = 100 if case_type and case_type.lower() in text else 50
        return round(min(100, semantic * 0.45 + overlap * 0.25 + statutory * 0.12 + authority * 0.1 + type_match * 0.08), 2)

    @classmethod
    def _paragraph(cls, text: str, issue: str, law: str) -> dict[str, Any]:
        paragraphs = [cls._clean(p) for p in re.split(r"\n\s*\n", text) if cls._clean(p)]
        terms = cls._terms(f"{issue} {law}")
        best = max(paragraphs, key=lambda p: len(terms & set(cls._terms(p))), default="")
        number = None
        match = re.match(r"(?:paragraph\s*)?(\d{1,4})[.)\s-]", best, re.I)
        if match:
            number = int(match.group(1))
        return {"number": number, "text": best, "source_text_available": bool(best)}

    @staticmethod
    def _outcome(text: str) -> str:
        patterns = [(r"bail\s+(?:is\s+)?granted", "Bail granted"), (r"bail\s+(?:is\s+)?rejected|bail\s+denied", "Bail rejected"),
                    (r"petition\s+(?:is\s+)?allowed", "Petition allowed"), (r"petition\s+(?:is\s+)?dismissed", "Petition dismissed"),
                    (r"appeal\s+(?:is\s+)?allowed", "Appeal allowed"), (r"appeal\s+(?:is\s+)?dismissed", "Appeal dismissed"),
                    (r"conviction\s+(?:is\s+)?upheld", "Conviction upheld"), (r"conviction\s+(?:is\s+)?set aside", "Conviction set aside"), (r"matter\s+(?:is\s+)?remanded", "Matter remanded")]
        for pattern, result in patterns:
            if re.search(pattern, text or "", re.I):
                return result
        return "Outcome could not be reliably extracted."

    @classmethod
    def _fact_comparison(cls, current: str, judgment: str) -> tuple[list[str], list[str]]:
        if not judgment:
            return [cls.INSUFFICIENT], [cls.INSUFFICIENT]
        current_terms, judgment_terms = cls._terms(current), cls._terms(judgment)
        shared = sorted(current_terms & judgment_terms)[:8]
        different = sorted((judgment_terms - current_terms))[:6]
        return ([f"Shared factual/legal concepts: {', '.join(shared)}."] if shared else [cls.INSUFFICIENT],
                [f"Judgment-only concepts requiring factual distinction: {', '.join(different)}."] if different else [cls.INSUFFICIENT])

    @staticmethod
    def _favorability(outcome: str, facts: str) -> str:
        if outcome == "Outcome could not be reliably extracted.": return "Neutral"
        seeking = any(word in facts.lower() for word in ("bail", "allow", "quash", "acquit", "relief"))
        if seeking and any(word in outcome.lower() for word in ("granted", "allowed", "set aside")): return "Favorable"
        if seeking and any(word in outcome.lower() for word in ("rejected", "dismissed", "upheld")): return "Unfavorable"
        return "Partially Favorable"

    @staticmethod
    def _favorability_reason(status: str, outcome: str) -> str:
        return f"Classified from the extracted outcome '{outcome}' and the stated case facts; this is not a prediction."

    @staticmethod
    def _insight(cases: list[dict], favorable: int, unfavorable: int) -> dict[str, Any]:
        favorable_terms = sorted({term for item in cases if item["favorability"] == "Favorable" for term in item["similar_facts"]})
        unfavorable_terms = sorted({term for item in cases if item["favorability"] == "Unfavorable" for term in item["similar_facts"]})
        return {"highly_similar_cases": sum(item["similarity_score"] >= 70 for item in cases), "favorable_cases": favorable,
            "unfavorable_cases": unfavorable, "common_factors_favorable": " ".join(favorable_terms) or CaseBriefService.INSUFFICIENT,
            "common_factors_unfavorable": " ".join(unfavorable_terms) or CaseBriefService.INSUFFICIENT,
            "important_factual_distinctions": " ".join(sorted({term for item in cases for term in item["distinguishing_facts"]})) or CaseBriefService.INSUFFICIENT,
            "important_legal_distinctions": "; ".join(sorted({item["court_reasoning"][:180] for item in cases})) or CaseBriefService.INSUFFICIENT}

    @staticmethod
    def _similarity_explanation(score: float) -> str:
        return "High similarity based on combined semantic retrieval, factual/legal term overlap, statutory fit, court authority, and case type." if score >= 70 else "Similarity is based on combined retrieval and available document metadata; verify the full judgment."

    @staticmethod
    def _terms(text: str) -> set[str]: return set(re.findall(r"[a-z]{4,}", (text or "").lower()))
    @staticmethod
    def _clean(text: Any) -> str: return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(text or "")))).strip()
    @staticmethod
    def _year(value: Any) -> int | None:
        try: return int(value) if value not in (None, "") else None
        except (TypeError, ValueError): return None
    @staticmethod
    def _within_years(year: int | None, start: int | None, end: int | None) -> bool: return (not start or (year and year >= start)) and (not end or (year and year <= end))
    @staticmethod
    def _extract_phrase(text: str, pattern: str) -> str: 
        match = re.search(pattern, text, re.I)
        return match.group(1).strip() if match else ""
    @staticmethod
    def _extract_sentences(text: str, pattern: str) -> str:
        return " ".join(sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if re.search(pattern, sentence, re.I))[:1500]

    def generate(self, db: Session, case_id: str) -> dict:
        doc = db.query(LegalDocument).filter((LegalDocument.external_id == case_id) | (LegalDocument.id == case_id)).first()
        if not doc:
            return {"error": "Judgment not found in the repository."}
        parts = process_judgment(doc.judgment_text or doc.extracted_text or "")
        source = legal_research_service._source(doc, 1)
        return {"case_information": {"case_name": doc.case_name or doc.title, "court": doc.court, "year": doc.year,
                                     "citation": doc.citation, "indian_kanoon_id": doc.external_id},
                "facts": parts["case_facts"] or doc.case_facts or "Not identified.",
                "legal_issues": parts["legal_issues"] or doc.legal_issues or "Not identified.",
                "arguments": parts["arguments"] or doc.arguments or "Not identified.",
                "law_applied": parts["acts_sections"] or doc.acts_sections or doc.acts or "Not identified.",
                "precedents": {"followed": [], "distinguished": []},
                "court_reasoning": parts["court_reasoning"] or doc.court_reasoning or "Not identified.",
                "ratio_decidendi": (parts["court_reasoning"] or doc.court_reasoning or doc.summary or "Not identified.")[:1200],
                "obiter_dicta": "Not identified from the extracted judgment text.",
                "final_decision": parts["final_decision"] or doc.final_decision or "Not identified.",
                "source_citation": source, "confidence_score": 85.0 if doc.judgment_text or doc.extracted_text else 45.0}


case_brief_service = CaseBriefService()
