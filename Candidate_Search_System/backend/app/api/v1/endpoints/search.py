import asyncio
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.search import SearchRequest, SearchResponse
from app.core.vector_search import vector_search
from app.core.gemini import gemini_client
from app.core.notifier import send_notification_background

logger = logging.getLogger(__name__)
router = APIRouter()


def parse_explanations(explanation_text: str, candidates: list) -> dict:
    result = {}
    if not explanation_text:
        return result

    parts = explanation_text.split("**")
    for i in range(1, len(parts) - 1, 2):
        name = parts[i].strip()
        text = parts[i + 1].strip() if (i + 1) < len(parts) else ""
        if name:
            result[name] = text

    missing = [c.get("name") for c in candidates if c.get("name") not in result]
    if missing:
        for line in explanation_text.splitlines():
            for name in missing:
                if name and name in line:
                    text = line[line.index(name) + len(name):].strip(" :-")
                    if text:
                        result[name] = text

    return result


def _build_item(candidate: dict, explanation: str) -> dict:
    return {
        "id": candidate.get("id"),
        "name": candidate.get("name", ""),
        "email": candidate.get("email"),
        "category": candidate.get("category"),
        "industry": candidate.get("industry"),
        "role": candidate.get("role"),
        "role_en": candidate.get("role_en"),
        "skills": candidate.get("skills", []),
        "experience_years": candidate.get("experience_years"),
        "education": candidate.get("education"),
        "additional_education": candidate.get("additional_education", []),
        "licenses": candidate.get("licenses", []),
        "location": candidate.get("location"),
        "languages": candidate.get("languages", []),
        "salary": candidate.get("salary"),
        "availability": candidate.get("availability"),
        "applicable_tes": candidate.get("applicable_tes"),
        "summary": candidate.get("summary"),
        "qualification_issues": candidate.get("qualification_issues", []),
        "match_score": candidate.get("score"),
        "explanation": explanation,
    }


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# ── Streaming endpoint ────────────────────────────────────────────────────────

@router.post("/search/stream")
async def search_candidates_stream(request: SearchRequest):
    """
    SSE endpoint. Events emitted:
      candidates   — immediately after vector search (~2-3 s)
      explanations — after Gemini finishes (~5-8 s)
      done         — stream complete
      error        — something went wrong
    """

    async def event_stream():
        try:
            vector_result = await asyncio.to_thread(
                vector_search.search_similar,
                request.query,
                industry=request.industry,
                salary_range=request.salary_range,
                location_filter=request.location_filter,
                role_keywords=request.role_keywords,
            )
        except Exception as exc:
            logger.error("Vector search failed: %s", exc)
            yield _sse("error", {"detail": "Vector search failed"})
            return

        if not vector_result:
            detail = (
                f"No {' or '.join(request.role_keywords)} found in the candidate collection."
                if request.role_keywords
                else "No candidates found matching your search."
            )
            yield _sse("error", {"detail": detail})
            return

        top_k = request.top_k or 5
        sorted_results = sorted(
            vector_result,
            key=lambda x: (x.get("experience_years") or 0, x.get("score") or 0),
            reverse=True,
        )[:top_k]

        candidate_items = [_build_item(c, "") for c in sorted_results]
        yield _sse("candidates", {
            "query": request.query,
            "results": candidate_items,
        })

        gemini_task = asyncio.create_task(
            asyncio.to_thread(gemini_client.generate_text, request.query, sorted_results)
        )
        notify_task = asyncio.create_task(
            send_notification_background(request, sorted_results)
        )

        raw_explanation = await gemini_task
        if raw_explanation:
            explanations = parse_explanations(raw_explanation, sorted_results)
            patches = {
                c.get("id"): (
                    explanations.get(c.get("name", ""))
                    or "AI explanation temporarily unavailable."
                )
                for c in sorted_results
            }
            yield _sse("explanations", {"patches": patches})
        else:
            logger.warning("Gemini returned no explanation.")

        asyncio.shield(notify_task)
        yield _sse("done", {})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Non-streaming fallback (N8N backward compat) ─────────────────────────────

@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_candidates(request: SearchRequest):
    vector_result = await asyncio.to_thread(
        vector_search.search_similar,
        request.query,
        industry=request.industry,
        salary_range=request.salary_range,
        location_filter=request.location_filter,
        role_keywords=request.role_keywords,
    )

    if not vector_result:
        raise HTTPException(status_code=404, detail="No candidates found")

    raw_explanation = await asyncio.to_thread(
        gemini_client.generate_text, request.query, vector_result
    )

    explanations = parse_explanations(raw_explanation or "", vector_result)

    response_items = []
    for candidate in vector_result:
        name = candidate.get("name", "")
        explanation = (
            explanations.get(name)
            or "AI explanation temporarily unavailable. Candidate data is still accurate."
        )
        response_items.append(_build_item(candidate, explanation))

    response_items.sort(
        key=lambda x: (x["experience_years"] or 0, x["match_score"] or 0),
        reverse=True,
    )

    top_k = request.top_k or 5
    return {"query": request.query, "results": response_items[:top_k]}