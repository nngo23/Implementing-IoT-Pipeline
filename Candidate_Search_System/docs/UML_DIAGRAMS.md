## UML class diagram (Backend)

```mermaid
classDiagram

class Candidate {
    +string id
    +string name
    +string role
    +string role_en
    +int experience_years
    +list skills
    +float salary
    +dict location
    +list licenses
    +list languages
    +list qualification_issues
}

class VoiceService {
    +parse_voice()
    +transcribe_audio()
}

class Parser {
    +parse_voice_command()
}

class SearchService {
    +search_stream()
}

class VectorSearch {
    +embed_texts()
    +search_similar()
}

class GeminiClient {
    +generate_explanations()
}

class Notifier {
    +send_notification_background()
}

class QdrantClient {
    +query_points()
}

class VoiceResponse {
    +bool success
    +string transcription
    +dict payload
    +string warning
    +bool block_stream
}

class SearchRequest {
    +string query
    +int top_k
    +dict salary_range
    +string industry
    +float location_filter
    +list role_keywords
    +bool role_detected
}

VoiceService --> Parser
VoiceService --> VoiceResponse

SearchService --> VectorSearch
VectorSearch --> QdrantClient

SearchService --> GeminiClient
SearchService --> Notifier

SearchService --> Candidate
SearchService --> SearchRequest
```

## N8N workflow diagram

```mermaid
flowchart TD
A[FastAPI /search/stream] --> B[Notifier (async)]

B --> C[POST → N8N Webhook]

C --> D[Switch: output_channel]

D -->|Slack| E[Send Slack Message]
D -->|Email| F[Send Email]

E --> G[End]
F --> G[End]
```
