# Risk management

| Risk                               | Impact | Likelihood | Mitigation                                                      |
| ---------------------------------- | ------ | ---------- | --------------------------------------------------------------- |
| Gemini API downtime                | High   | Medium     | Implement retry logic, fallback message                         |
| Qdrant vector search errors        | High   | Low        | Regular backups, monitor logs                                   |
| Whisper transcription inaccuracies | Medium | Medium     | Use medium model, validate transcription                        |
| N8N webhook failure                | High   | Low        | Enable webhook retry, alert notifications                       |
| Docker service failure             | Medium | Low        | Docker health checks, restart policies                          |
| Data privacy concerns              | High   | Low        | Do not store real candidate emails, mask sensitive info         |
| Timeline slippage                  | Medium | Medium     | Weekly Gantt review, adjust tasks, prioritize critical features |
