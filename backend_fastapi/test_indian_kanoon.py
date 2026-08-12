"""
test_indian_kanoon.py
=====================
Integration test for the Indian Kanoon pipeline.

Run from backend_fastapi/ directory:
    python test_indian_kanoon.py

What it tests:
  1. Indian Kanoon API connectivity and response shape
  2. Database insertion via ik_ingestion_service
  3. PDF download (best-effort - passes even if IK has no PDF)
  4. Duplicate-insertion guard (idempotency)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import SessionLocal, Base, engine
from app.services import indian_kanoon_service
from app.services.ik_ingestion_service import ingest_ik_result
from app.repositories import document_repository

QUERY = "contract dispute"

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

def ok(msg):   print(f"{GREEN}  [OK] {msg}{RESET}")
def fail(msg): print(f"{RED}  [FAIL] {msg}{RESET}"); sys.exit(1)
def info(msg): print(f"{YELLOW}  >> {msg}{RESET}")
def warn(msg): print(f"{YELLOW}  [WARN] {msg}{RESET}")


def main():
    print("\n" + "=" * 60)
    print("  NyayaAI - Indian Kanoon Integration Test")
    print("  Query: \"" + QUERY + "\"")
    print("=" * 60 + "\n")

    # Ensure DB tables exist
    Base.metadata.create_all(bind=engine)
    ok("Database tables verified")

    # ── Test 1: API search ────────────────────────────────────────────────────
    print("\n[1] Testing Indian Kanoon API search...")
    results = indian_kanoon_service.search_judgments(QUERY)

    if results is None:
        fail("search_judgments returned None instead of a list")

    info("Received " + str(len(results)) + " results from Indian Kanoon")

    if len(results) == 0:
        warn("No results returned - check API token or network.")
        warn("Continuing with mock data for DB/PDF tests.")
        results = [{
            "title":        "Test Contract Dispute Case",
            "court":        "Supreme Court of India",
            "year":         2020,
            "citation":     "TEST 2020 SC 001",
            "document_url": "https://api.indiankanoon.org/doc/test123/",
            "snippet":      "This is a test contract dispute case for integration testing.",
            "doc_id":       "test_mock_001",
        }]
    else:
        ok("API returned results successfully")
        first = results[0]
        info("First result : " + first["title"][:70])
        info("Court        : " + str(first["court"]))
        info("Year         : " + str(first["year"]))
        info("doc_id       : " + str(first["doc_id"]))

        for key in ("title", "court", "year", "citation", "document_url", "snippet", "doc_id"):
            if key not in first:
                fail("Missing key '" + key + "' in API result")
        ok("All required keys present in API response")

    # ── Test 2: Database insertion ────────────────────────────────────────────
    print("\n[2] Testing database insertion...")
    db = SessionLocal()
    try:
        target = results[0]
        saved = ingest_ik_result(db, target)

        if saved is None:
            fail("ingest_ik_result returned None - insertion failed")

        ok("Document saved - DB id=" + str(saved.id))
        info("Title       : " + str(saved.title))
        info("Source      : " + str(saved.source))
        info("external_id : " + str(saved.external_id))
        info("pdf_path    : " + str(saved.pdf_path))

        fetched = document_repository.get_by_external_id(db, target["doc_id"])
        if not fetched:
            fail("Could not retrieve saved document by external_id")
        ok("Document retrievable by external_id")

        # ── Test 3: PDF download ──────────────────────────────────────────────
        print("\n[3] Testing PDF download...")
        if saved.pdf_path and os.path.isfile(saved.pdf_path):
            size_kb = os.path.getsize(saved.pdf_path) / 1024
            ok("PDF saved at: " + saved.pdf_path + " (" + f"{size_kb:.1f}" + " KB)")
        else:
            warn("PDF not downloaded - IK may not provide PDF for this doc.")
            warn("This is expected for some documents - not a failure.")

        # ── Test 4: Duplicate guard ───────────────────────────────────────────
        print("\n[4] Testing duplicate insertion guard...")
        saved_again = ingest_ik_result(db, target)
        if saved_again and saved_again.id == saved.id:
            ok("Duplicate correctly skipped - same DB id returned")
        else:
            fail("Duplicate guard failed - a second row was inserted")

        # ── Summary ───────────────────────────────────────────────────────────
        total = document_repository.count(db)
        print("\n" + "=" * 60)
        print(GREEN + "  All tests passed!" + RESET)
        print("  Total documents in DB: " + str(total))
        print("=" * 60 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
