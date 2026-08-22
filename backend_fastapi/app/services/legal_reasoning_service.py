"""Rule-based judicial reasoning extraction built on the existing case pipeline."""

import re
from typing import Any

from app.services.case_processing_service import process_judgment


class LegalReasoningService:
    def extract(self, judgment) -> dict[str, Any]:
        text = judgment.judgment_text or judgment.extracted_text or ""
        parts = process_judgment(text) if text else {}
        reasoning = parts.get("court_reasoning") or judgment.court_reasoning or ""
        decision = parts.get("final_decision") or judgment.final_decision or ""
        return {
            "case": self._case_metadata(judgment),
            "flow": [
                {"stage": "Facts", "content": parts.get("case_facts") or judgment.case_facts or "Not identified."},
                {"stage": "Issues", "content": parts.get("legal_issues") or judgment.legal_issues or "Not identified."},
                {"stage": "Applicable Laws", "content": parts.get("acts_sections") or judgment.acts_sections or "Not identified."},
                {"stage": "Arguments", "content": parts.get("arguments") or judgment.arguments or "Not identified."},
                {"stage": "Evidence Evaluation", "content": self._extract_evidence(text)},
                {"stage": "Court Reasoning", "content": reasoning or "Not identified."},
                {"stage": "Ratio Decidendi", "content": self.identify_ratio_decidendi(reasoning, decision)},
                {"stage": "Obiter Dicta", "content": self.identify_obiter(text, reasoning)},
                {"stage": "Final Decision", "content": decision or "Not identified."},
            ],
            "ratio_decidendi": self.identify_ratio_decidendi(reasoning, decision),
            "obiter_dicta": self.identify_obiter(text, reasoning),
            "confidence_score": 0.82 if reasoning and decision else 0.55,
            "source_citation": {"case_name": judgment.case_name or judgment.title, "paragraph_number": self._paragraph_number(text, reasoning), "indian_kanoon_id": judgment.external_id, "link": judgment.document_url},
        }

    def identify_ratio_decidendi(self, reasoning: str, decision: str) -> str:
        source = reasoning or decision
        sentences = self._sentences(source)
        signal = [s for s in sentences if re.search(r"\b(hold|therefore|we find|we conclude|principle|must|shall)\b", s, re.I)]
        return " ".join((signal or sentences)[-2:])[:1200] or "No ratio could be extracted from the available text."

    def identify_obiter(self, text: str, reasoning: str) -> str:
        sentences = self._sentences(reasoning or text)
        observations = [s for s in sentences if re.search(r"\b(observe|observation|incidentally|however|clarif|note that)\b", s, re.I)]
        return " ".join(observations[:3])[:1200] or "No distinct obiter dicta identified."

    @staticmethod
    def _extract_evidence(text: str) -> str:
        matches = [s for s in LegalReasoningService._sentences(text) if re.search(r"\b(evidence|proof|testimony|witness|record|material)\b", s, re.I)]
        return " ".join(matches[:3])[:1200] or "No separate evidence-evaluation section identified."

    @staticmethod
    def _sentences(text: str) -> list[str]:
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if len(s.strip()) > 30]

    @staticmethod
    def _paragraph_number(text: str, excerpt: str) -> int:
        paragraphs = [p for p in re.split(r"\n\s*\n", text or "") if p.strip()]
        return next((index + 1 for index, paragraph in enumerate(paragraphs) if excerpt and excerpt[:60] in paragraph), 1)

    @staticmethod
    def _case_metadata(judgment) -> dict[str, Any]:
        return {"id": judgment.external_id or str(judgment.id), "title": judgment.title, "court": judgment.court, "year": judgment.year, "citation": judgment.citation}


legal_reasoning_service = LegalReasoningService()
