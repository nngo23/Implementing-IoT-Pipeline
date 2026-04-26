# Risk Management

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Gemini API downtime | High | Medium | Auto-fallback to `models/gemini-2.5-flash` on 404; graceful message on 429 quota errors; SSE stream unaffected (explanations are async) |
| Gemini quota exceeded | Medium | Medium | Returns `"AI explanation temporarily unavailable (quota reached)."` — candidate data still displayed |
| Qdrant vector search errors | High | Low | Strict role filter returns empty rather than wrong results; regular backups; monitor logs |
| Whisper transcription inaccuracies | Medium | Medium | `correct_words()` post-processing fixes common ASR errors; Whisper `medium` model used for accuracy |
| N8N webhook failure | High | Low | Fire-and-forget notifier never blocks SSE stream; webhook retry can be enabled in N8N; `httpx` timeout/error logged |
| N8N sending invalid payload | Medium | Low | `send_notification_background()` enforces strict validation (industry, role_keywords, recipient_email) before sending |
| Voice endpoint returning bad queries to search | High | Low | Hard gates in `/voice` — `block_stream=true` prevents frontend from calling search without a valid role + industry |
| Docker service failure | Medium | Low | Docker health checks and restart policies; Whisper model loaded once at startup to survive restarts gracefully |
| Data privacy concerns | High | Low | No real candidate emails stored; mock data only; sensitive info masked |
| Timeline slippage | Medium | Medium | Weekly Gantt review, adjust tasks, prioritize critical features |
| Audio upload failures (wrong format) | Low | Low | Content-type validation in `/voice` — 400 error returned immediately for non-audio files |
| Hardcoded geo-center (Lahti) | Low | Medium | Documented as known limitation; configurable in future via request parameter |
| Seniority not distinguished in role filter | Medium | High | `role_en` substring match ignores "senior"/"junior" qualifiers; all experience levels returned for both queries. Mitigation: add seniority tier parsing to `parsers.py` and a minimum `experience_years` filter in `vector_search.py` |
| City-based location search returns no results | High | High | Geo-filter center is hardcoded to Lahti 15520; `parse_location_filter()` only extracts km radius — city names in queries are not parsed or geocoded. Searching "nurses in Helsinki" applies no location filter at all and may return candidates anywhere. Mitigation: add city-to-coordinates lookup in `parsers.py` and make the geo-filter center dynamic in `vector_search.py` |
