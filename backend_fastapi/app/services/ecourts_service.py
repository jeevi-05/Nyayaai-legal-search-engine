"""Server-side eCourtsIndia advocate activity integration."""

from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Any
from urllib.parse import quote, unquote

import httpx
from loguru import logger

from app.core.config import get_settings


class ECourtsSearchError(Exception):
    """Safe error for citizen-facing lawyer search."""


class ECourtsService:
    cache_ttl = 120
    max_page_size = 25
    max_aggregation_pages = 5

    def __init__(self) -> None:
        self._search_cache: dict[tuple, tuple[float, dict[str, Any]]] = {}
        self._lawyer_cache: dict[str, dict[str, Any]] = {}
        self._case_cache: dict[str, dict[str, Any]] = {}

    def search_cases(self, params: dict[str, Any]) -> dict[str, Any]:
        settings = get_settings()
        if not settings.ECOURTS_API_TOKEN.strip():
            raise ECourtsSearchError("Lawyer search is temporarily unavailable. Please try again later.")
        normalized = self._normalize_params(params)
        requested_page = normalized["page"]
        requested_size = normalized["page_size"]
        normalized["page"] = 1
        normalized["page_size"] = self.max_page_size
        key = tuple(sorted({**normalized, "requested_page": requested_page, "requested_size": requested_size}.items()))
        cached = self._search_cache.get(key)
        if cached and time.monotonic() - cached[0] < self.cache_ttl:
            return cached[1]
        all_records: list[dict[str, Any]] = []
        upstream_has_next = True
        total_cases = 0
        response_status = 0
        for upstream_page in range(1, self.max_aggregation_pages + 1):
            normalized["page"] = upstream_page
            records, total, has_next, response_status = self._request_page(settings, normalized)
            all_records.extend(records)
            total_cases = total
            upstream_has_next = has_next
            lawyers_seen = len(self.aggregate_advocates(all_records))
            if not has_next or lawyers_seen >= requested_page * requested_size:
                break
        lawyer_results = self.aggregate_advocates(all_records)
        start = (requested_page - 1) * requested_size
        page_results = lawyer_results[start:start + requested_size]
        advocate_names = {name for record in all_records for name in self.extract_advocates(record)}
        logger.info(
            "eCourts lawyer search query='{}' status={} cases={} advocates_extracted={} first_advocate='{}'",
            normalized["legal_issue"] or normalized["advocate_name"] or "",
            response_status,
            len(all_records),
            len(advocate_names),
            next(iter(advocate_names), ""),
        )
        result = {"results": page_results, "page": requested_page, "pageSize": requested_size, "total": len(lawyer_results), "lawyerTotal": len(lawyer_results), "caseTotal": total_cases, "hasNextPage": start + requested_size < len(lawyer_results) or upstream_has_next, "lawyerAggregationComplete": not upstream_has_next or len(all_records) >= self.max_aggregation_pages * self.max_page_size}
        self._search_cache[key] = (time.monotonic(), result)
        return result

    def _request_page(self, settings: Any, params: dict[str, Any]) -> tuple[list[dict[str, Any]], int, bool, int]:
        try:
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                response = client.get(
                    f"{settings.ECOURTS_API_BASE_URL.rstrip('/')}/api/partner/search",
                    params=self._query_params(params),
                    headers={"Authorization": f"Bearer {settings.ECOURTS_API_TOKEN}", "Accept": "application/json"},
                )
        except httpx.RequestError as exc:
            raise ECourtsSearchError("Lawyer search is temporarily unavailable. Please try again in a moment.") from exc
        if response.status_code >= 400:
            raise ECourtsSearchError("Lawyer search is temporarily unavailable. Please try again in a moment.")
        try:
            payload = response.json()
        except ValueError as exc:
            raise ECourtsSearchError("Lawyer search is temporarily unavailable. Please try again in a moment.") from exc
        records, total, has_next = self._records(payload, params["page_size"])
        return records, total, has_next, response.status_code

    def get_lawyer(self, lawyer_id: str) -> dict[str, Any] | None:
        cached = self._lawyer_cache.get(lawyer_id)
        if cached:
            return cached
        name = self._normalize_name(unquote(lawyer_id))
        try:
            result = self.search_cases({"advocate_name": name, "page": 1, "page_size": self.max_page_size})
        except ECourtsSearchError:
            return None
        return self._lawyer_cache.get(quote(name, safe="")) or next((item for item in result["results"] if item["name"] == name), None)

    def get_case(self, cnr: str) -> dict[str, Any] | None:
        cached = self._case_cache.get(cnr)
        if cached:
            return cached
        settings = get_settings()
        if not settings.ECOURTS_API_TOKEN.strip():
            return None
        try:
            with httpx.Client(timeout=15, follow_redirects=True) as client:
                response = client.get(
                    f"{settings.ECOURTS_API_BASE_URL.rstrip('/')}/api/partner/case/{quote(cnr, safe='')}",
                    headers={"Authorization": f"Bearer {settings.ECOURTS_API_TOKEN}", "Accept": "application/json"},
                )
            if response.status_code >= 400:
                return None
            payload = response.json()
        except ECourtsSearchError:
            return None
        except (httpx.RequestError, ValueError):
            return None
        data = payload.get("data", payload) if isinstance(payload, dict) else payload
        detail = data.get("courtCaseData", data) if isinstance(data, dict) else {}
        case = self.normalize_case(detail)
        case["history"] = detail.get("historyOfCaseHearings") or detail.get("listingDates")
        case["judges"] = detail.get("judges")
        case["orders"] = detail.get("judgmentOrders") or detail.get("interimOrders")
        case["notices"] = detail.get("notices")
        case["caseNumber"] = detail.get("caseNumber")
        case["cnr"] = case["cnr"] or cnr
        self._case_cache[cnr] = case
        return case

    @staticmethod
    def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
        def clean(value: Any, limit: int) -> str:
            return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]
        return {
            "legal_issue": clean(params.get("legal_issue"), 300), "state": clean(params.get("state"), 100),
            "district": clean(params.get("district"), 100), "court": clean(params.get("court"), 160),
            "case_type": clean(params.get("case_type"), 100), "case_status": clean(params.get("case_status"), 100),
            "practice_area": clean(params.get("practice_area"), 100), "advocate_name": clean(params.get("advocate_name"), 160),
            "page": max(1, min(int(params.get("page") or 1), 1000)),
            "page_size": max(1, min(int(params.get("page_size") or 10), 25)),
        }

    @staticmethod
    def _query_params(params: dict[str, Any]) -> dict[str, Any]:
        query = {"page": params["page"], "pageSize": params["page_size"]}
        if params["advocate_name"]:
            query["advocates"] = params["advocate_name"]
        elif params["legal_issue"] and re.fullmatch(r"[A-Z][A-Za-z.'-]{2,}", params["legal_issue"]):
            query["advocates"] = params["legal_issue"]
        elif params.get("force_query") or params["legal_issue"]:
            query["query"] = params["legal_issue"]
        for key in ("state", "district", "court", "case_type", "case_status"):
            if params[key]:
                query[key] = params[key]
        return query

    @classmethod
    def _records(cls, payload: Any, page_size: int) -> tuple[list[dict[str, Any]], int, bool]:
        records: list[dict[str, Any]] = []
        container = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), dict) else payload
        if isinstance(container, dict):
            for key in ("results", "cases", "records", "items"):
                value = container.get(key)
                if isinstance(value, list):
                    records.extend(item for item in value if isinstance(item, dict))
                    break
        elif isinstance(payload, list):
            records = [item for item in payload if isinstance(item, dict)]
        total = cls._integer(container, ("totalHits", "total", "totalCount", "count", "recordsTotal")) or len(records)
        has_next = cls._boolean(container, ("hasNextPage", "hasNext", "nextPage"))
        return records[:page_size], total, bool(has_next if has_next is not None else len(records) >= page_size and len(records) < total)

    @staticmethod
    def _integer(payload: Any, keys: tuple[str, ...]) -> int | None:
        if not isinstance(payload, dict): return None
        for key in keys:
            try:
                if payload.get(key) is not None: return int(payload[key])
            except (TypeError, ValueError): pass
        return None

    @staticmethod
    def _boolean(payload: Any, keys: tuple[str, ...]) -> bool | None:
        if not isinstance(payload, dict): return None
        return next((payload[key] for key in keys if isinstance(payload.get(key), bool)), None)

    def extract_advocates(self, record: dict[str, Any]) -> list[str]:
        names = []
        for key, value in record.items():
            if "advocate" not in key.lower(): continue
            entries = value if isinstance(value, list) else [value]
            for entry in entries:
                name = entry.get("name") if isinstance(entry, dict) else entry
                normalized = self._normalize_name(name)
                if normalized and normalized not in names: names.append(normalized)
        return names

    def aggregate_advocates(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            case = self.normalize_case(record)
            if case["cnr"]: self._case_cache[case["cnr"]] = case
            for advocate in self.extract_advocates(record): grouped[advocate].append(case)
        results = []
        for name, cases in grouped.items():
            lawyer_id = quote(name, safe="")
            courts = sorted({case["court"] for case in cases if case["court"]})
            states = sorted({case["state"] for case in cases if case["state"]})
            districts = sorted({case["district"] for case in cases if case["district"]})
            pending = sum(self._pending(case["status"]) for case in cases)
            lawyer = {"id": lawyer_id, "name": name, "photoUrl": None, "email": None, "phone": None, "whatsapp": None, "verified": None, "barCouncil": None, "barId": None, "locations": list(filter(None, districts + states)), "state": states[0] if states else None, "district": districts[0] if districts else None, "courts": courts, "practiceAreas": [], "relatedCaseCount": len(cases), "courtActivity": {"totalCases": len(cases), "pendingCases": pending, "disposedCases": len(cases) - pending}, "cases": cases, "source": "eCourtsIndia"}
            self._lawyer_cache[lawyer_id] = lawyer
            results.append(lawyer)
        return sorted(results, key=lambda item: (-item["relatedCaseCount"], item["name"].lower()))

    @classmethod
    def normalize_case(cls, record: dict[str, Any]) -> dict[str, Any]:
        def value(*keys: str) -> Any:
            for key in keys:
                for actual, candidate in record.items():
                    if actual.lower() == key.lower() and candidate not in (None, ""): return candidate
            return None
        advocates = []
        for key, candidate in record.items():
            if "advocate" in key.lower():
                values = candidate if isinstance(candidate, list) else [candidate]
                advocates.extend(str(item.get("name") if isinstance(item, dict) else item) for item in values if item)
        return {"cnr": value("cnr", "cnrNumber", "caseNumber"), "title": value("caseTitle", "title", "caseName"), "court": value("courtName", "court", "court_name"), "caseType": value("caseType", "case_type"), "status": value("caseStatus", "status"), "filingNumber": value("filingNumber", "filing_number"), "petitioners": value("petitioners", "petitionersName"), "respondents": value("respondents", "respondentsName"), "advocates": advocates, "acts": value("acts", "actsAndSections", "actsSections", "sections"), "category": value("caseCategory", "category", "case_category"), "filingDate": value("filingDate", "filing_date"), "decisionDate": value("decisionDate", "decision_date"), "nextHearingDate": value("nextHearingDate", "next_hearing_date"), "hearings": value("hearings", "caseHistory"), "orders": value("orders", "ordersAvailable"), "hasOrders": bool(value("hasOrders", "ordersAvailable", "orders_available")), "hasJudgments": bool(value("hasJudgments", "judgmentsAvailable", "judgments_available")), "state": value("state"), "district": value("district")}

    @staticmethod
    def _normalize_name(value: Any) -> str:
        normalized = re.sub(r"[.,]", " ", str(value or ""))
        normalized = re.sub(r"[^\w &'()-]", " ", normalized)
        return re.sub(r"\s+", " ", normalized).strip(" ;-").upper()[:160]

    @staticmethod
    def _pending(status: Any) -> bool:
        return bool(status and any(word in str(status).lower() for word in ("pending", "active", "ongoing", "hearing", "admitted")))


ecourts_service = ECourtsService()
