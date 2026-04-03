# API documentation - Candidate search API

## Base URL

http://localhost:8000/api/v1

---

## 1. Health check

GET /health

Response:

```json
{
  "status": "ok"
}
```

## 2. Search API

sequenceDiagram
participant User
participant Frontend
participant Backend
participant Embedding
participant Qdrant
participant Gemini

    User->>Frontend: Enter query
    Frontend->>Backend: POST /search

    Backend->>Embedding: Generate vector
    Embedding-->>Backend: Vector

    Backend->>Qdrant: Search candidates
    Qdrant-->>Backend: Top 20

    Backend->>Backend: Sort by experience

    Backend->>Gemini: Generate explanation
    Gemini-->>Backend: Text

    Backend-->>Frontend: Top 5 + explanation

POST /search

Request

```json
{
  "query": "welder with ISO certification",
  "top_k": 5,
  "salary_range": { "min": 3000, "max": 6000 },
  "industry": "Teollisuus",
  "location_filter": 40
}
```

### Logic

- Retrieve top 20 candidates
- Sort by experience → score
- Return top 5

## 3. Voice API

sequenceDiagram
participant User
participant Frontend
participant Backend
participant Whisper
participant Parser
participant N8N
participant SearchAPI

    User->>Frontend: Speak command
    Frontend->>Backend: POST /voice (audio)

    Backend->>Whisper: Transcribe audio
    Whisper-->>Backend: Text

    Backend->>Parser: Extract parameters
    Parser-->>Backend: Structured query

    Backend->>N8N: Send payload

    N8N->>SearchAPI: POST /search
    SearchAPI-->>N8N: Candidates

    N8N-->>User: Email / Slack results

POST /voice

### Query params

- output_channel: email | slack
- recipient_email: required if email

### Flow

1. Audio upload
2. Whisper transcription
3. Query parsing
4. Send to N8N

Response

```json
{
  "transcription": "Find welders 40 km salary 3000 to 6000",
  "payload": {...}
}
```

## 4. Voice health

GET /voice_health

### Supported industries

- Teollisuus
- HoReCa
- Rakennusala
- ICT / Teknologia
- Terveydenhuolto
- Logistiikka

### Error codes

| Code | Meaning          |
| ---- | ---------------- |
| 200  | Success          |
| 400  | Bad request      |
| 422  | Validation error |
| 500  | Server error     |
