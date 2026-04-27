## Versioning

Git branch:
main – Stable production-ready version

Git tag:

- v1.0 — Initial release
- v1.0.1 — latest update with streaming and validation improvements

## Release notes (v1.0.1)

### New features:

- Streaming search (/search/stream): real-time results using Server-Sent Events, with candidates shown first and AI explanations added shortly after
- Strict voice validation: queries must include both a role and an industry; invalid inputs are blocked early
- Asynchronous notifications: Slack and email delivery handled via N8N in the background
- Precise role filtering: ensures results match the requested role only

### Improvements:

- Jina v3 embeddings: improved semantic search accuracy with a single loaded model
- Optimized search performance: reduced Qdrant workload and early exit when industry is missing
- Frontend enhancements: cleaner error display, better guidance for voice input, and faster feedback with streaming UI
- Efficiency gains: early validation avoids unnecessary processing

### Breaking changes:

- Replaced /search with /search/stream
- /voice now handles validation only
- Backend sends results to N8N instead of being triggered by it

### Known issues:

- Seniority not distinguished (e.g. senior vs junior roles)
- Location filtering is limited to a fixed center point
- Some roles are missing from keyword mapping
- No authentication
- Uses synthetic candidate data

## Release notes (v1.0)

### Features

- Voice-based candidate search with Slack/email output
- AI-generated match explanations (Gemini 2.5 Flash)
- Experience-based ranking
- N8N workflow for automated distribution
- Pre-filled interview email generation

### Improvements

- Optimized Qdrant search (1024-d embeddings)
- Improved Whisper transcription (medium model)
- Enhanced UI for voice interaction

### Known issues

- No authentication
- Mock dataset only
