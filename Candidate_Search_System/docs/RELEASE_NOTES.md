## Versioning

Git branch: `main` — stable, production-ready

Git tag: `v1.0.1` — final submission

---

## Release notes (v1.0.1)

### New features

- **SSE streaming search** — `/search/stream` emits `candidates` event within ~2–3 s, followed by `explanations` patches once Gemini finishes (~5–8 s). Frontend renders cards immediately with skeleton loaders for AI analysis.
- **Voice command search** — audio recorded as WebM/Opus at 16 kHz, transcribed via Whisper `medium`, parsed into structured query parameters.
- **Strict role + industry gate** — `/voice` returns `block_stream=true` if no role or industry is detected; frontend is blocked from triggering search on invalid queries.
- **Strict role filter on vector results** — results must match at least one `role_keywords` value against `role_en`; hard failure returns 0 results (no wrong-role fallback).
- **Professional standard query enrichment** — before embedding, the query is enriched with `min_education` and `mandatory_licenses` from the `professional_standards` Qdrant collection for the matched industry.
- **AI-powered candidate explanations** — Gemini 2.5 Flash generates 4–5 sentence per-candidate match analysis; auto-fallback on model 404 and quota 429 errors.
- **N8N fire-and-forget notifier** — results sent to Slack or email via N8N webhook without blocking the SSE stream; strict pre-send validation prevents malformed payloads.
- **Gmail compose integration** — each candidate card includes a pre-filled interview invitation link for Gmail.
- **Interview invitation email** — frontend provides direct Gmail compose links per candidate; N8N handles bulk distribution to Slack/email channels.

### Improvements

- Whisper model loaded once at server startup — eliminates 1–3 s cold-start on first voice request.
- `correct_words()` post-processing fixes common ASR transcription errors before parsing.
- `INDUSTRY_ROLE_ONTOLOGY` phrase-first matching resolves ambiguous roles (e.g. "software developer" → ICT before fallback keyword map).
- `VoiceResponse.block_stream` flag gives the frontend explicit control — no guessing from HTTP status.
- Notifier skips silently when `N8N_WEBHOOK_URL` is not configured (safe for local dev).
- Gemini client auto-retries once with fallback model on 404; logs quota/client errors without crashing.
- Frontend renders candidates immediately with skeleton loaders; `explanations` SSE event patches cards in-place by candidate `id`.
- `searchAPI.jsx` / `WaveRecorder.jsx` abort controller prevents duplicate SSE streams on repeated recordings.

### Known issues

- Authentication not implemented (development only — no auth on any endpoint).
- Location geo-filter center is hardcoded to Lahti (60.9634°N, 25.6712°E); not user-configurable.
- Only mock candidate data for Finnish industry roles.
- Non-streaming `/search` endpoint used by N8N does not apply the SSE streaming pattern — Gemini call is blocking.
- **No seniority distinction** — searching for "senior IT developer" and "IT developer" returns identical results. The role filter matches against `role_en` using substring presence (e.g. `"software developer" in role_text`), so seniority qualifiers like "senior", "junior", or "lead" are ignored entirely. The ranking is also unaffected — `experience_years` sorting applies the same logic regardless of seniority level requested. A candidate with 2 years of experience and a candidate with 10 years are treated as equally valid matches for both queries; only their sort position differs.
- **City-based location search not supported** — the geo-filter in `vector_search.py` is hardcoded to a single fixed center point (Lahti 15520, 60.9634°N, 25.6712°E) with a radius in km. Searching for roles "in Helsinki" or "in Tampere" returns no results because the parser only extracts a distance radius (e.g. "within 40 km") and always measures it from Lahti — city names in the query are not parsed or resolved to coordinates. Any query that relies on a city name rather than a km radius will return 0 candidates.
