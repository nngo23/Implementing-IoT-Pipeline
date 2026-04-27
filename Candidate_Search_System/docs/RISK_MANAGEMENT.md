# Risk management

| Risk                                        | Impact | Likelihood | Mitigation                                                         |
| ------------------------------------------- | ------ | ---------- | ------------------------------------------------------------------ |
| Gemini API instability                      | High   | Medium     | Return candidates first; run explanation generation asynchronously |
| Qdrant search failures                      | High   | Low        | Add monitoring and logs; provide safe fallback responses           |
| Whisper transcription inaccuracies          | Medium | Medium     | Enforce strict role and industry validation before processing      |
| Vague or invalid voice commands             | Medium | High       | Reject early in `/voice` with clear user-facing warning messages   |
| SSE stream interruptions                    | Medium | Medium     | Implement robust error handling and UI fallback states             |
| N8N workflow instability                    | Medium | Low        | Keep decoupled from core flow; rely on built-in retry mechanisms   |
| Duplicate or inconsistent UI error states   | Low    | Medium     | Centralise frontend error handling logic                           |
| Fixed location logic                        | Medium | Medium     | Document limitation; future improvement for dynamic geo parsing    |
| Missing role keyword coverage (e.g. welder) | Medium | Medium     | Expand role mapping and enforce strict role filtering              |
| Synthetic dataset limitations               | Medium | High       | Clearly label mock data; plan real-world data integration          |
| Missing authentication layer                | High   | Medium     | Restrict access during development; add auth in future             |
| Project scope or timeline drift             | Medium | Medium     | Prioritise stability of core voice-to-search pipeline              |
