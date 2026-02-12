## Candidate Search System

A full-stack candidate search tool using AI reasoning, vector search, and adaptive UI for web.
Frontend interacts with a FastAPI backend to search candidates intelligently and display results with AI-generated explanations.

## 🚀 Features

🧠 AI-powered candidate matching

📊 Filter-based search (salary, industry, location)

✍️ AI explanations for match reasoning

📈 Feedback loop to improve AI matching

🔗 Frontend: React + Material UI

🗂 Backend: FastAPI + Qdrant + Sentence Transformers + Google Gemini AI

## 🗂 Table of Contents

    System Requirements

    Installation

    Configuration

    Running the Application

    Frontend Overview

    Backend API Reference

    Usage Examples

    Error Handling

    Contributing

    License

## 🔧 System Requirements

Component Version / Requirement
Python ≥ 3.12
Node.js ≥ 18
FastAPI 0.121.x
Uvicorn 0.38.x
React 18+
Material UI 5+
Qdrant 1.16.x
Sentence Transformers 5.2.x
Google Gemini API Key Required
Docker & Docker Compose Optional but recommended

## 🛠 Installation

1. Backend

Install Python dependencies:

    pip install -r requirements.txt

requirements.txt

    fastapi==0.121.1
    uvicorn[standard]==0.38.0
    pydantic==2.12.4
    qdrant-client==1.16.2
    sentence-transformers==5.2.0
    google-genai==1.56.0
    python-dotenv==1.2.1

2. Frontend

Install Node dependencies:

    cd frontend
    npm install

## ⚙️ Configuration

Backend

    Start Qdrant database (Docker Compose):

        cd path/to/Project/backend
        docker compose -f docker-compose.db.yml up -d

    Create a .env file at the backend root:

        QDRANT_HOST=localhost
        QDRANT_PORT=6333
        GOOGLE_API_KEY=your_google_gemini_api_key
        MODEL_NAME=all-mpnet-v2

Frontend

    Update API URL in searchAPI.js:

        const API_BASE = "http://localhost:8000/api/v1";

    Optional: configure Teams Bot webhook or ngrok URL for testing.

## ▶️ Running the Application

Backend

    Development mode:

        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

    Production mode:

        uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Frontend

    Development mode:

    npm start

## 🖥 Frontend Overview

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

UX Features:

    Scrollable candidate list

    Input validation warnings for better results

    Feedback buttons to improve AI matching

## 📡 Backend API Reference

    Base URL
    http://localhost:8000/api/v1

1.  Health Check

    GET /health
    Response:

        {
        "status": "healthy",
        "version": "1.0.0",
        "qdrant": {"status": "ok","collection":"candidates"}
        }

2.  Search Candidates

    POST /search

        Request Body:

        {
        "query": "Experienced welder with MIG/MAG and TIG methods",
        "top_k": 5,
        "salary_range": {"min":3000,"max":6000},
        "industry": "Teollisuus",
        "location_filter": 40.5
        }

    Response: top 5 candidates with fields:

        name, role, skills

        experience_years, education

        match_score, explanation

        location & salary

        Optional feedback

3.  Send Feedback

    POST /feedback

        {
        "candidate_id": "candidate_079",
        "feedback_type": "up",
        "reason": "Highly qualified and skilled"
        }

## 🧾 Usage Examples

    JavaScript (Axios)
        import { searchCandidates, sendFeedbackAPI } from './searchAPI';

        const results = await searchCandidates({
        query: "Welder ISO 9606-1 TIG MIG",
        top_k: 5,
        salary_range: { min: 3000, max: 6000 },
        industry: "Teollisuus",
        location_filter: 40
        });

        await sendFeedbackAPI({
        candidateId: results[0].id,
        feedbackType: "up",
        reason: "Excellent fit"
        });

## Python (Requests)

    import requests

    payload = {
    "query": "Welder ISO 9606-1 TIG MIG",
    "top_k": 5,
    "salary_range": {"min":3000,"max":6000},
    "industry":"Teollisuus",
    "location_filter":40
    }
    res = requests.post("http://localhost:8000/api/v1/search", json=payload)
    print(res.json())

## ❗Error Handling

    Code Meaning
    200 OK
    404 No candidates found
    422 Invalid request body
    500 Internal server error

## 🤝 Contributing

    Fork the repository
    Create a feature branch: git checkout -b feat/xyz
    Commit your changes
    Open a pull request

## 📝 License

Open source – see the LICENSE file.
