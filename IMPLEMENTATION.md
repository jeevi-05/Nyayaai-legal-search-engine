# NyayaAI Legal Research Engine - Production Implementation

## Overview

This document describes the production implementation of the NyayaAI Legal Research Engine, which converts the prototype into a production-level legal research platform using only:
1. Indian Kanoon API
2. Backend database repository
3. AI processing pipeline

## Implementation Summary

### Task 1: Backend PDF Download API Fix

**File Modified:** `backend_fastapi/app/api/research.py`

**Endpoint:** `GET /api/research/case/{case_id}/download`

**Changes:**
- Fixed 404 error by implementing proper error handling
- Added fallback PDF generation from `judgment_text` when Indian Kanoon doesn't provide a PDF
- Returns proper HTTP status codes:
  - 200: Success - PDF file downloaded
  - 404: Case not found or judgment text unavailable
  - 500: Server error during PDF generation

**Workflow:**
```
Case ID
    ↓
Fetch case information from database
    ↓
Check if PDF already exists (cached)
    ↓
If not cached:
    ↓
Generate PDF from judgment_text using reportlab
    ↓
Save PDF path to database
    ↓
Return FileResponse with PDF
```

### Task 2: Indian Kanoon Service Updates

**File Modified:** `backend_fastapi/app/services/indian_kanoon_service.py`

**Functions Implemented:**

1. **fetch_document_details(case_id)**
   - Fetches case metadata from Indian Kanoon API
   - Returns: title, court, date, citation, acts, sections, judgment metadata

2. **fetch_document_text(case_id)**
   - Fetches complete judgment text
   - Handles cases where Indian Kanoon provides:
     - Case metadata only
     - Case metadata + judgment text
     - PDF

3. **generate_case_pdf(case_id)**
   - Generates PDF using reportlab
   - Flow: case_id → fetch details → fetch judgement text → create structured PDF → save PDF path → return generated file location

### Task 3: PDF Generation Service

**File Modified:** `backend_fastapi/app/services/pdf_download_service.py`

**Features:**
- Tries to download PDF from Indian Kanoon first
- Falls back to generating PDF from `judgment_text` if unavailable
- Uses `reportlab` library for PDF generation
- Generates structured PDF with:
  1. Case Title
  2. Court Name
  3. Date
  4. Citation
  5. Acts and Sections
  6. Case Facts
  7. Legal Issues
  8. Arguments
  9. Court Reasoning
  10. Final Judgment
  11. Complete Judgment Text

**PDF Filename Format:** `<case_name>_<doc_id>.pdf`

**Example:** `Vishaka_State_of_Rajasthan_12345.pdf`

### Task 4: Remove Dataset Dependency

**Files to Remove:**
- `backend_fastapi/app/dataset/` directory
- `backend_fastapi/app/services/dataset_loader.py`

**Search and Replace:**
- Remove imports of `dataset`
- Remove references to `cases.json`
- Remove references to `sample_data`

**Updated Services:**
- `backend_fastapi/app/services/ik_ingestion_service.py` - Updated to always generate PDF from judgment_text

### Task 5: Database Cleanup Script

**File Created:** `backend_fastapi/scripts/clear_existing_cases.py`

**Purpose:**
- Removes dummy cases
- Removes manually inserted documents
- Removes sample PDF records

**Does NOT delete:**
- Database schema
- Tables
- Relationships
- Embeddings structure

**Usage:**
```bash
cd backend_fastapi
python scripts/clear_existing_cases.py
```

### Task 6: Repository Pipeline Update

**File Modified:** `backend_fastapi/app/api/research.py`

**Add to Repository Workflow:**
```
Indian Kanoon Case
    ↓
Fetch complete judgement
    ↓
Generate structured information
    ↓
Generate PDF from judgment_text
    ↓
Extract text from PDF
    ↓
Create embedding
    ↓
Save document to database
```

**Database Record Stores:**
- case_id
- title
- court
- year
- acts
- sections
- judgment_text
- pdf_path
- embedding

### Task 7: Frontend PDF Download Fix

**File Modified:** `frontend/src/pages/CaseDetailPage.jsx`

**Changes:**
- Added proper loading state: "Generating PDF..."
- Added error handling with UI notifications:
  - 404: "Judgement PDF could not be generated."
  - 500: "Server error while generating PDF."
  - Other: "Download failed. Please try again."
- Replaced `alert()` with proper UI notification
- Added PDF error display component

### Task 8: Full Judgment View

**Already Implemented:**
- Search Case
- Open Case Details
- View Full Judgment

**Displays:**
- Title
- Court
- Date
- Citation
- Facts
- Issues
- Acts
- Sections
- Arguments
- Reasoning
- Final Judgment
- Complete Judgment Text

## Testing

### TEST 1: Search Vishaka
```bash
curl -X GET "http://localhost:8000/api/research/search?query=Vishaka"
```

**Expected:** Case loads from Indian Kanoon API

### TEST 2: Open Case Details
```bash
curl -X GET "http://localhost:8000/api/research/case/{case_id}"
```

**Expected:** Shows Facts, Issues, Acts, Sections, Judgment

### TEST 3: View Full Judgment
```bash
curl -X GET "http://localhost:8000/api/research/case/{case_id}"
```

**Expected:** Complete judgment text appears

### TEST 4: Download PDF
```bash
curl -X GET "http://localhost:8000/api/research/case/{case_id}/download" \
  -H "Authorization: Bearer <token>" \
  --output Vishaka_State_of_Rajasthan.pdf
```

**Expected:** PDF downloads successfully

### TEST 5: Add to Repository
```bash
curl -X POST "http://localhost:8000/api/research/case/{case_id}/add-to-repository" \
  -H "Authorization: Bearer <token>"
```

**Expected:** Case added successfully with all fields populated

## Environment Variables

Required in `.env`:
```env
# PostgreSQL
DATABASE_URL=sqlite:///./nyayaai.db

# JWT
JWT_SECRET=nyayaai-super-secret-key-for-jwt-signing-must-be-256-bits-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# App
APP_NAME=NyayaAI Legal Search Engine
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:3000

# File Upload
MAX_UPLOAD_SIZE_MB=50
UPLOAD_DIR=uploads

# Indian Kanoon API
INDIAN_KANOON_API_TOKEN=<your_api_token>
```

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Search Page  │  │ Case Detail  │  │ Repository   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API Routes                            │   │
│  │  - /api/research/search                                  │   │
│  │  - /api/research/case/{id}                               │   │
│  │  - /api/research/case/{id}/download                      │   │
│  │  - /api/research/case/{id}/add-to-repository             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │                      Services Layer                        │  │
│  │  ┌──────────────────┐  ┌──────────────────┐              │  │
│  │  │ Indian Kanoon    │  │ PDF Download     │              │  │
│  │  │ Service          │  │ Service          │              │  │
│  │  └──────────────────┘  └──────────────────┘              │  │
│  │  ┌──────────────────┐  ┌──────────────────┐              │  │
│  │  │ Case Processing  │  │ Embedding        │              │  │
│  │  │ Service          │  │ Service          │              │  │
│  │  └──────────────────┘  └──────────────────┘              │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │                   Repository Layer                         │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │              Database (SQLite/PostgreSQL)            │  │  │
│  │  │  - legal_documents table                             │  │  │
│  │  │  - case_id, title, court, year                       │  │  │
│  │  │  - acts, sections, judgment_text                     │  │  │
│  │  │  - pdf_path, embedding                               │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Indian Kanoon API                             │
│  - Search judgments                                            │
│  - Fetch document metadata                                     │
│  - Fetch document text                                         │
│  - Fetch PDF (when available)                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

1. **No Manual Data:** All data comes from Indian Kanoon API
2. **PDF Fallback:** Always generates PDF from judgment_text if Indian Kanoon doesn't provide one
3. **Structured Extraction:** Uses rule-based extraction for:
   - Acts and Sections
   - Case Facts
   - Legal Issues
   - Arguments
   - Court Reasoning
   - Final Judgment
4. **Database Persistence:** All documents stored with embeddings for semantic search
5. **Error Handling:** Proper HTTP status codes and user-friendly error messages

## Dependencies

**Backend:**
- fastapi==0.111.0
- uvicorn[standard]==0.29.0
- sqlalchemy==2.0.30
- reportlab>=4.0.0
- httpx==0.27.0
- loguru==0.7.2
- sentence-transformers==2.7.0

**Frontend:**
- react-router-dom
- axios
- lucide-react

## Migration Instructions

1. **Remove dataset folder:**
   ```bash
   rm -rf backend_fastapi/app/dataset/
   ```

2. **Remove dataset loader:**
   ```bash
   rm backend_fastapi/app/services/dataset_loader.py
   ```

3. **Run database cleanup:**
   ```bash
   cd backend_fastapi
   python scripts/clear_existing_cases.py
   ```

4. **Restart backend:**
   ```bash
   cd backend_fastapi
   uvicorn app.main:app --reload
   ```

5. **Test the implementation:**
   - Search for a case
   - Open case details
   - Download PDF
   - Add to repository

## Troubleshooting

**PDF not downloading:**
- Check if `judgment_text` is populated in database
- Verify `reportlab` is installed: `pip install reportlab`
- Check backend logs for errors

**Case not found:**
- Verify Indian Kanoon API token is set
- Check network connectivity to Indian Kanoon API
- Review backend logs for API errors

**Database errors:**
- Run cleanup script: `python scripts/clear_existing_cases.py`
- Check database file permissions
- Verify DATABASE_URL in .env

## Future Enhancements

1. Add LLM-based extraction for better accuracy
2. Implement caching layer for frequently accessed cases
3. Add PDF preview in browser before download
4. Implement batch download for multiple cases
5. Add case comparison features
