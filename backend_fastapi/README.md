# NyayaAI Legal Search Engine — FastAPI Backend

Production-ready FastAPI backend replacing the Spring Boot backend.
The React frontend at `../frontend` requires **no changes** — all endpoints and response shapes are identical.

---

## Tech Stack

| Layer        | Technology                             |
|--------------|----------------------------------------|
| Framework    | FastAPI 0.111 + Uvicorn                |
| ORM          | SQLAlchemy 2.0                         |
| Migrations   | Alembic                                |
| Database     | PostgreSQL                             |
| Auth         | python-jose (JWT) + passlib (bcrypt)  |
| Validation   | Pydantic v2                            |
| Logging      | Loguru                                 |
| PDF parsing  | PyPDF2 / pdfplumber (Phase 2)         |

---

## Quick Start

### 1. Create virtual environment
```bash
cd backend_fastapi
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
Edit `.env` and set your PostgreSQL credentials:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/nyayaai
```

### 4. Create the database
```sql
CREATE DATABASE nyayaai;
```

### 5. Run database migrations (optional — app auto-creates tables on startup)
```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 6. Start the server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

The server starts at **http://localhost:8080**.
Interactive API docs: **http://localhost:8080/docs**

---

## API Endpoints

| Method | Path                              | Auth     | Role  |
|--------|-----------------------------------|----------|-------|
| GET    | /api/health                       | Public   | —     |
| POST   | /api/auth/register                | Public   | —     |
| POST   | /api/auth/login                   | Public   | —     |
| GET    | /api/user/me                      | JWT      | Any   |
| GET    | /api/dashboard                    | JWT      | Any   |
| GET    | /api/documents                    | Public   | —     |
| GET    | /api/documents/{id}               | Public   | —     |
| GET    | /api/documents/count              | Public   | —     |
| GET    | /api/documents/category/{cat}     | Public   | —     |
| POST   | /api/documents/upload             | JWT      | ADMIN |
| DELETE | /api/documents/{id}               | JWT      | ADMIN |

---

## Dataset Auto-Loader

On every startup the server scans:
```
app/dataset/acts/
app/dataset/landmark_cases/
app/dataset/judgments/
```
New `.json` and `.pdf` files are parsed and inserted into PostgreSQL.
Duplicates are skipped automatically.

---

## Phase 2 Placeholders

The following services are stubbed and ready for implementation:

- `app/services/semantic_search_service.py` — LegalBERT + FAISS/ChromaDB
- `app/services/embedding_service.py` — HuggingFace transformers
- `app/services/rag_service.py` — Llama 3 RAG pipeline
- `app/services/knowledge_graph_service.py` — Neo4j entity graph

---

## Project Structure

```
backend_fastapi/
├── app/
│   ├── main.py                  # FastAPI app + lifespan
│   ├── api/                     # Route handlers
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic v2 schemas
│   ├── services/                # Business logic
│   ├── repositories/            # DB access layer
│   ├── core/                    # Config, DB, JWT, security
│   ├── middleware/              # Auth dependency injection
│   └── dataset/                 # Seed data (JSON/PDF)
├── alembic/                     # Migration environment
├── requirements.txt
├── .env
└── alembic.ini
```
