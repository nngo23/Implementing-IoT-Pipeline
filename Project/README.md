## Adaptive AI Candidate Search System

An intelligent, self-improving candidate retrieval system that combines semantic vector search, feedback-driven dynamic ranking, and LLM-based explanation generation.

Built with:

    FastAPI backend
    Qdrant vector database
    Jina Embeddings v3
    Google Gemini LLM
    React + Material UI frontend

## Overview

This project implements a hybrid semantic retrieval pipeline for candidate matching.

Unlike traditional keyword search systems, this engine:

    Uses dense vector embeddings for semantic similarity
    Dynamically adjusts ranking using recruiter feedback
    Enriches queries using professional standards
    Generates explainable AI reasoning for each candidate
    Continuously improves through a feedback loop

## System architecture

```java
User query
    ↓
Query enrichment (professional standards)
    ↓
Embedding generation (Jina v3)
    ↓
Vector search (Qdrant)
    ↓
Feedback-based score adjustment
    ↓
LLM explanation layer (Gemini)
    ↓
Ranked & explained results
```

## Key features

    🧠 Semantic AI matching

    Uses Jina embeddings v3
    Vector similarity search via Qdrant
    Cosine similarity ranking

    📊 Smart filtering

    Salary range
    Industry
    Location radius (geo filtering)

    📈 Adaptive Feedback Optimization

    Recruiter feedback influences ranking weights
    Dynamic score multiplier
    Improves over time without retraining embeddings

    🧾 Explainable AI

    Google Gemini generates match explanations
    Increases recruiter trust
    Structured reasoning per candidate

    🖥 Modern frontend

    React 18
    Material UI 5+
    Interactive filtering panel
    Candidate cards with skill badges
    Thumbs up/down feedback system

## Tech stack

| Layer            | Technology                |
| ---------------- | ------------------------- |
| Backend          | FastAPI                   |
| Vector DB        | Qdrant                    |
| Embeddings       | jinaai/jina-embeddings-v3 |
| LLM              | Google Gemini             |
| ORM              | SQLAlchemy                |
| Database         | PostgreSQL                |
| Frontend         | React + MUI               |
| Containerization | Docker                    |

## 🔧 System requirements

| Component | Requirement                      |
| --------- | -------------------------------- |
| Python    | ≥ 3.12                           |
| Node.js   | ≥ 18                             |
| Docker    | Optional                         |
| GPU       | Optional (for torch CUDA builds) |

## 🛠 Installation

1. Backend setup

Install Python dependencies:

```bash
    pip install -r requirements.txt
```

Start Qdrant

```bash
    docker compose -f docker-compose.db.yml up -d
```

Create .env file

```ini
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=candidates
QDRANT_COLLECTION_PROFESSIONALSTANDARD=professional_standards
GOOGLE_API_KEY=your_google_api_key
```

2. Frontend setup

```bash
   cd frontend
   npm install
   npm run dev
```

## ▶️ Running the application

Backend

    Development mode:

        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

    Production mode:

        uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Frontend

    Development mode:

    npm run dev

## 📡 Backend API reference

    Base URL
    http://localhost:8000/api/v1

1.  Health check

    GET /health
    Response:

    ```json
    {
      "status": "healthy",
      "version": "1.0.0",
      "qdrant": {
        "status": "ok",
        "collection": "candidates_collection",
        "collection": "professional_standards_collection"
      }
    }
    ```

2.  Search candidates

    POST /search

        Request Body:

        ```json
            {
            "query": "Experienced welder with MIG/MAG and TIG methods",
            "top_k": 5,
            "salary_range": {"min":3000,"max":6000},
            "industry": "Teollisuus",
            "location_filter": 40.5
            }
        ```
        Response

        ```json
                {
                "query": "...",
                "results": [
                    {
                    "id": "candidate_001",
                    "name": "John Doe",
                    "match_score": 87.3,
                    "skills": ["TIG", "MIG"],
                    "experience_years": 8,
                    "salary": 5200,
                    "explanation": "Strong alignment with required welding certifications..."
                    }
                ]
                }
        ```

    👍 Send feedback

    POST /feedback

    ```json
    {
      "candidate_id": "candidate_079",
      "feedback_type": "up",
      "reason": "Highly qualified and certified"
    }
    ```

    Feedback updates:
    Ranking bonus multiplier
    Query optimization hints
    Dynamic scoring weight

## 🔁 Adaptive ranking mechanism

Final score formula:

    Final Score = Vector Similarity Score × Feedback Weight Multiplier

Where:

    Feedback Weight = 1 + (positive_feedback - negative_feedback) × α

This allows:

    Real-time ranking improvement
    No embedding retraining required
    Lightweight learning-to-rank behavior

## 🧠 AI explanation pipeline

Gemini receives:

    Original query
    Enriched query context
    Ranked candidate list

It returns:

    Structured reasoning
    Match justification
    Highlighted strengths

## 🖥 Frontend overview

FilterPanel: salary slider, industry dropdown, distance input

PromptPanel: AI prompts for:

    Minimum criteria
    Location
    Special professional skills & qualities
    Experience length & education level (same line)
    Must-have qualities

CandidateCard: shows top 5 candidates with:

    Match score
    Skills badges
    AI explanation
    Optional feedback (thumb up/down with explanation)

UX features:

    Scrollable candidate list
    Input validation warnings for better results
    Feedback buttons to improve AI matching

## 📊 Error handling

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 404  | No candidates found   |
| 422  | Validation error      |
| 500  | Internal server error |

## 🧪 Research contributions

This system demonstrates:

    Hybrid semantic retrieval
    Feedback-driven ranking optimization
    Explainable AI integration
    Query enrichment via professional standards
    Modular AI microservice architecture

## 📦 Future improvements

    Hybrid lexical + vector search
    A/B testing for ranking strategies
    Bayesian feedback weighting
    Embedding caching layer
    Async LLM batching
    Kubernetes deployment

## 🤝 Contributing

```bash
    git checkout -b feature/new-feature
    git commit -m "Add new feature"
    git push
```

Open a pull request.

## 📜 License

Open source – see LICENSE file.
