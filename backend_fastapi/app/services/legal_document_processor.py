"""Normalise, validate, segment and enrich Indian Kanoon judgments."""

import html
import json
import re
from datetime import datetime

from app.services.embedding_service import EmbeddingService


class LegalDocumentProcessor:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def process(self, raw_text: str, metadata: dict | None = None) -> dict:
        text = self.clean_judgment_text(raw_text)
        extracted = self.extract_case_metadata(text, metadata or {})
        entities = self.extract_legal_entities(text)
        sections = self.segment_judgment_sections(text)
        return {"text": text, "metadata": extracted, "entities": entities, "sections": sections, "paragraphs": self.number_paragraphs(text), "embedding": self.generate_embeddings(text)}

    @staticmethod
    def clean_judgment_text(raw_text: str) -> str:
        text = html.unescape(raw_text or "")
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()

    def extract_case_metadata(self, text: str, supplied: dict) -> dict:
        title = supplied.get("title", "")
        case_name = title if self._valid_case_name(title) else self._case_name_from_text(text)
        date = supplied.get("date", "")
        year = supplied.get("year") or self._valid_year(date) or self._valid_year(text[:1500])
        return {"case_name": case_name or title or "Untitled", "court": supplied.get("court", ""), "bench": supplied.get("judges", "") or self._bench(text), "date": date, "year": year, "citation": supplied.get("citation", "")}

    @staticmethod
    def extract_legal_entities(text: str) -> dict:
        acts = list(dict.fromkeys(re.findall(r"\b(?:Constitution of India|Indian Penal Code|Code of Criminal Procedure|[A-Z][A-Za-z ]{2,80} Act(?:,? \d{4})?)\b", text, re.I)))[:30]
        sections = list(dict.fromkeys(re.findall(r"\b(?:Article|Section|Ss?\.)\s*\d+[A-Za-z-]*\b", text, re.I)))[:50]
        parties = list(dict.fromkeys(re.findall(r"\b([A-Z][A-Za-z.&' ]{1,70}\s+(?:v\.?|vs\.?|versus)\s+[A-Z][A-Za-z.&' ]{1,70})\b", text)))[:10]
        citations = list(dict.fromkeys(re.findall(r"\b(?:\(?\d{4}\)?\s*\d*\s*(?:SCC|AIR|CriLJ)\s*\d+)\b", text, re.I)))[:30]
        return {"acts": acts, "sections": sections, "parties": parties, "citations": citations}

    @staticmethod
    def segment_judgment_sections(text: str) -> dict:
        labels = {"facts": r"\b(facts?|background)\b", "issues": r"\b(issues?|questions? (?:of law|for determination))\b", "arguments": r"\b(arguments?|submissions?|contentions?)\b", "reasoning": r"\b(reasoning|analysis|discussion|consideration)\b", "decision": r"\b(order|conclusion|decision|result|disposed)\b"}
        output = {}
        for name, pattern in labels.items():
            match = re.search(pattern + r".{0,2500}", text, re.I | re.S)
            output[name] = match.group(0).strip() if match else ""
        return output

    @staticmethod
    def number_paragraphs(text: str) -> list[dict]:
        chunks = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 25]
        return [{"number": index + 1, "text": paragraph} for index, paragraph in enumerate(chunks)]

    def generate_embeddings(self, text: str) -> list[float]:
        return self.embedding_service.embed(text[:8000]) if text else []

    @staticmethod
    def _valid_case_name(value: str) -> bool:
        return bool(re.match(r"^[^\n]{2,100}\s+(?:v\.?|vs\.?|versus)\s+[^\n]{2,100}$", (value or "").strip(), re.I)) and not bool(re.search(r"\bSection\s+\d+", value, re.I))

    def _case_name_from_text(self, text: str) -> str:
        for candidate in re.findall(r"(?m)^\s*([^\n]{3,150}\s+(?:v\.?|vs\.?|versus)\s+[^\n]{3,150})\s*$", text[:4000], re.I):
            if self._valid_case_name(candidate): return candidate.strip()
        return ""

    @staticmethod
    def _bench(text: str) -> str:
        match = re.search(r"(?:CORAM|BEFORE|BENCH)\s*:?\s*([^\n]{3,250})", text[:3000], re.I)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _valid_year(value: str) -> int | None:
        match = re.search(r"\b(19\d{2}|20\d{2})\b", value or "")
        if match and 1900 <= int(match.group(1)) <= datetime.now().year: return int(match.group(1))
        return None


legal_document_processor = LegalDocumentProcessor()
