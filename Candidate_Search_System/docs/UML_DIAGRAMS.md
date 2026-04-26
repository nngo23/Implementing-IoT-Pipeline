# UML Diagrams

## UML Class Diagram (Backend)

```mermaid
classDiagram

class Candidate {
    +string id
    +string name
    +string email
    +string role
    +string role_en
    +string industry
    +string category
    +int experience_years
    +list skills
    +int salary
    +dict location
    +dict education
    +list additional_education
    +list licenses
    +list languages
    +string availability
    +string applicable_tes
    +string summary
    +list qualification_issues
}

class SearchRequest {
    +string query
    +int top_k
    +dict salary_range
    +string industry
    +float location_filter
    +list role_keywords
    +bool role_detected
    +string output_channel
    +string recipient_email
    +normalize_salary()
    +normalize_industry()
    +normalize_location()
    +normalize_channel()
    +enforce_role_consistency()
}

class SearchResponse {
    +string query
    +list results
}

class VoiceResponse {
    +bool success
    +string transcription
    +dict payload
    +string warning
    +bool block_stream
    +dict n8n_response
    +float processing_time
    +string error
}

class SearchService {
    +search_candidates_stream(request) StreamingResponse
    +search_candidates(request) SearchResponse
    +parse_explanations(text, candidates) dict
}

class VoiceService {
    +parse_voice(audio, output_channel, recipient_email) VoiceResponse
    +health_check() dict
}

class Parser {
    +parse_voice_command(text, output_channel, recipient_email) dict
    +parse_industry(text) str
    +parse_role_keywords(text) list
    +parse_salary_range(text) dict
    +parse_location_filter(text) float
    +parse_top_k(text) int
    +correct_words(text) str
}

class GeminiClient {
    +string model
    +generate_text(prompt, candidates) str
    +format_candidates(candidates) str
}

class VectorSearch {
    +search_similar(query, top_k, industry, salary_range, location_filter, role_keywords) list
    +embed_texts(texts) list
}

class Notifier {
    +send_notification_background(request, candidates) None
}

VoiceService --> Parser
VoiceService --> VoiceResponse
SearchService --> VectorSearch
SearchService --> GeminiClient
SearchService --> Notifier
SearchService --> Candidate
SearchRequest --> SearchResponse
Parser --> SearchRequest
```

---

## Sequence Diagram — Streaming Search (SSE)

```mermaid
sequenceDiagram
    participant Frontend
    participant SearchService
    participant VectorSearch
    participant Gemini
    participant Notifier

    Frontend->>SearchService: POST /search/stream (JSON body)
    SearchService->>VectorSearch: search_similar(query, filters)
    VectorSearch-->>SearchService: raw results (up to 20)

    SearchService->>SearchService: strict role filter (role_en match)
    SearchService->>SearchService: sort by experience → score
    SearchService-->>Frontend: SSE event: candidates

    par Async tasks
        SearchService->>Gemini: generate_text(query, top5)
        SearchService->>Notifier: send_notification_background()
    end

    Gemini-->>SearchService: explanation text
    SearchService->>SearchService: parse_explanations → patches by id
    SearchService-->>Frontend: SSE event: explanations
    SearchService-->>Frontend: SSE event: done
```

---

## Sequence Diagram — Voice Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant VoiceService
    participant Whisper
    participant Parser

    User->>Frontend: Tap record
    Frontend->>Frontend: Capture WebM audio (16 kHz AudioContext)
    User->>Frontend: Tap stop

    Frontend->>VoiceService: POST /voice (multipart audio)
    VoiceService->>VoiceService: Save temp .webm file
    VoiceService->>Whisper: Convert → 16 kHz mono WAV → transcribe
    Whisper-->>VoiceService: raw text

    VoiceService->>Parser: correct_words → parse_voice_command
    Parser-->>VoiceService: structured payload

    alt role_detected = false
        VoiceService-->>Frontend: success=false, block_stream=true, warning
        Frontend->>Frontend: Show error, do NOT call search
    else industry = null
        VoiceService-->>Frontend: success=false, block_stream=true, warning
        Frontend->>Frontend: Show error, do NOT call search
    else valid
        VoiceService-->>Frontend: success=true, block_stream=false, payload
        Frontend->>Frontend: POST /search/stream with payload
    end
```

---

## N8N Workflow Diagram

```mermaid
flowchart TD
    A[Webhook Trigger — POST from notifier.py] --> B[HTTP Request POST /search]

    B --> C[Switch: output_channel]

    C -->|slack| D[Send Slack Message — top 5 candidates]
    C -->|email| E[Send Email — top 5 candidates]

    D --> F[End]
    E --> F[End]
```

**N8N send conditions (enforced in notifier.py):**
- `industry` must be present
- `role_keywords` must be present
- If `output_channel=email`, `recipient_email` must be provided
- Results list must not be empty
- `N8N_WEBHOOK_URL` must be configured

---

## State Diagram — Frontend Search Session

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Recording : user taps Start
    Recording --> Transcribing : user taps Stop
    Transcribing --> Idle : voice error / empty transcription
    Transcribing --> Idle : block_stream=true (bad query)
    Transcribing --> Searching : success=true, block_stream=false
    Searching --> Complete : SSE candidates event received
    Searching --> Idle : SSE error event received
    Complete --> Complete : SSE explanations event patches cards
    Complete --> Idle : user taps Reset
```
