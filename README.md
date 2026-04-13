# RPR — AI Research Paper Refinement System

A production-ready SaaS application that refines academic research papers using a multi-stage AI pipeline powered by Groq LLM.

---

## Architecture

```text
User → Frontend (HTML/JS) → FastAPI Backend → MongoDB
                                    ↓
                          BackgroundTask (Async)
                                    ↓
                    Parser → Splitter → Humanizer
                                    ↓
                    Paraphraser → Grammar → Reconstruct
                                    ↓
                          Groq LLM (llama3-8b-8192)
                                    ↓
                          Output DOCX → Download
```

---

## Tech Stack

| Layer      | Technology                             |
|------------|----------------------------------------|
| Backend    | FastAPI, Python 3.11                   |
| Database   | MongoDB (Motor async driver)           |
| Auth       | JWT (python-jose) + bcrypt             |
| AI/LLM     | Groq API (llama3-8b-8192)              |
| Embeddings | Sentence Transformers (MiniLM)         |
| Frontend   | HTML, CSS, Vanilla JS                  |
| Infra      | Docker, docker-compose                 |
| Queue      | FastAPI BackgroundTasks (Redis-ready)  |

---

## Quick Start

### 1. Prerequisites

- Docker & docker-compose
- Groq API key → <https://console.groq.com>

### 2. Configure environment

```bash
cp .env .env.local
# Edit .env — set GROQ_API_KEY and SECRET_KEY
```

### 3. Run with Docker

```bash
docker-compose up --build
```

App available at: <http://localhost:8000>

---

## Local Development (without Docker)

### 1. Activate venv

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start MongoDB locally

```bash
# Update .env: MONGO_URI=mongodb://localhost:27017
mongod
```

### 4. Run backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 5. Open frontend

Navigate to <http://localhost:8000/pages/index.html>

---

## API Reference

### Auth

| Method | Endpoint           | Description        |
|--------|--------------------|--------------------|
| POST   | /api/auth/signup   | Register user      |
| POST   | /api/auth/login    | Login, get JWT     |
| GET    | /api/auth/me       | Get current user   |

### Jobs

| Method | Endpoint                    | Description           |
|--------|-----------------------------|-----------------------|
| POST   | /api/upload                 | Upload file, start job|
| GET    | /api/status/{job_id}        | Poll job status       |
| GET    | /api/jobs                   | List user's jobs      |
| GET    | /api/process/{job_id}/logs  | Get pipeline logs     |
| GET    | /api/download/{job_id}      | Download refined DOCX |
| GET    | /api/health                 | Health check          |

---

## AI Pipeline Stages

1. **Parse** — Extract text from PDF/DOCX/TXT
2. **Split** — Detect sections (Abstract, Introduction, etc.) or chunk by paragraphs
3. **Humanize** — Rewrite to sound natural using Groq LLM
4. **Paraphrase** — Restructure sentences to reduce similarity
5. **Grammar** — Improve academic tone and fix errors
6. **Reconstruct** — Assemble refined sections into DOCX output

---

## Project Structure

```text
RPR/
├── backend/app/
│   ├── main.py              # FastAPI app entry point
│   ├── auth/                # JWT auth, routes, dependencies
│   ├── routes/              # upload, status, process, download, health
│   ├── services/            # parser, splitter, humanizer, paraphraser, grammar, pipeline
│   ├── llm/                 # Groq client, prompts
│   ├── models/              # Pydantic models
│   ├── db/                  # MongoDB, Redis connections
│   ├── core/                # Settings, security
│   └── utils/               # file_utils, embeddings, logger
├── frontend/
│   ├── pages/               # index, login, signup, dashboard, processing, result
│   ├── js/                  # api, auth, upload, process, status, download
│   └── css/                 # styles, auth, dashboard
├── data/                    # uploads/, outputs/, temp/
├── docker/backend.Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## Environment Variables

| Variable                      | Description                        |
|-------------------------------|------------------------------------|
| SECRET_KEY                    | JWT signing secret                 |
| GROQ_API_KEY                  | Groq API key                       |
| GROQ_MODEL                    | Model name (llama3-8b-8192)        |
| MONGO_URI                     | MongoDB connection string          |
| MONGO_DB                      | Database name                      |
| REDIS_URL                     | Redis URL (optional)               |
| UPLOAD_DIR / OUTPUT_DIR       | File storage paths                 |

---

## Notes

- Similarity score is semantic cosine similarity (0–1). Lower = more variation from original.
- The system **preserves academic meaning** — it does not guarantee plagiarism removal.
- Max file size: 20MB.
- Supported formats: PDF, DOCX, DOC, TXT.
