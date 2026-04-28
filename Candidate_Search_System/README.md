# Candidate Search API - Recruitment AI Platform

## Overview

AI-powered recruitment system using voice search, vector database, and LLM explanations.

---

## Features

- Voice search (English & Finnish)
- AI candidate matching (Qdrant)
- Gemini AI explanations
- Email/Slack delivery (N8N)
- Experience-first ranking

---

## Tech Stack

- FastAPI
- Qdrant
- Gemini 2.5 Flash
- Whisper
- N8N
- React

---

## Setup

### 1. Clone

```bash
git clone https://github.com/nngo23/Implementing-IoT-Pipeline/tree/61acaa2f1b642db4449a170698defad9df201bac/Candidate_Search_System
cd sandbox1
```

### 2. Start services

```bash
docker compose -f docker-compose.db.yml up -d
docker compose -f docker-compose.service.yml up -d
```

### 3. Backend

```bash
cd backend
pip install -r requirements.txt
python scripts/setup_professionalStandard.py
python scripts/setup_qdrant.py
uvicorn app.main:app --reload
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### Architecture

See docs/ARCHITECTURE.md

### API Docs

See docs/API_DOCUMENTATION.md

### Versioning

v1.0 → Initial submission
v1.0.1 → latest update with streaming and validation improvements

### Notes

- Mock data only
- No authentication
- Designed for demo purposes

### Author

Kimberton AI Studio

## Documentation

- Architecture → docs/ARCHITECTURE.md
- API → docs/API_DOCUMENTATION.md
- UML Diagrams → docs/UML_DIAGRAMS.md
- Project management → docs/PROJECT_MANAGEMENT.md
- Risk management → docs/RISK_MANAGEMENT.md
- Versioning & release documentation → docs/RELEASE_NOTES.md
- UX/UI design documentation → docs/UX_UI_DESIGN.md
