from fastapi import APIRouter, HTTPException
from app.schemas.search import SearchRequest, SearchResponse
from app.core.vector_search import vector_search 
from app.core.gemini import gemini_client  
import logging

from app.config import Config

logger = logging.getLogger(__name__)
router = APIRouter()

def parse_explanations(explanation_text: str, candidates: list) -> dict:
    """
    Parse Gemini's response into a {candidate_name: explanation} dict.

    Gemini returns something like:
        **Markku Pääkkönen** Some explanation text...
        **Minna Saarinen** Some explanation text...

    This parser is tolerant: it tries the **bold** split first, then falls
    back to a line-by-line search so a slightly different format doesn't
    silently produce None for every candidate.
    """
    result = {}
    if not explanation_text:
        return result

    # Strategy 1: split on ** markers (original approach, fixed)
    parts = explanation_text.split("**")
    # parts: ['', 'Name', ' explanation text ', 'Name2', ' explanation text2 ', ...]
    for i in range(1, len(parts) - 1, 2):
        name = parts[i].strip()
        text = parts[i + 1].strip() if (i + 1) < len(parts) else ""
        if name:
            result[name] = text

    # Strategy 2: for any candidate still missing, search line by line
    missing = [c.get("name") for c in candidates if c.get("name") not in result]
    if missing:
        for line in explanation_text.splitlines():
            for name in missing:
                if name and name in line:
                    # Use the rest of the line after the name as the explanation
                    text = line[line.index(name) + len(name):].strip(" :-")
                    if text:
                        result[name] = text

    return result


@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_candidates(request: SearchRequest):
    # BUG FIX: Removed bare `except Exception as e: raise HTTPException(...)`.
    # That pattern swallowed the full traceback before it could reach the global
    # exception handler in main.py, making all 500s invisible/undebuggable.
    # Specific, expected errors are still caught and returned as proper HTTP errors.

    vector_result = vector_search.search_similar(
        request.query,
        industry=request.industry,
        salary_range=request.salary_range,
        location_filter=request.location_filter
    )

    if not vector_result:
        raise HTTPException(status_code=404, detail="No candidates found")

    raw_explanation = gemini_client.generate_text(request.query, vector_result)
    if not raw_explanation:
        logger.warning("Gemini returned no explanation (quota exceeded or error). Candidates will be returned without AI explanations.")

    # BUG FIX: The original parser split on "**" and did a strict name equality check.
    # If Gemini's response format varied slightly, explanation_text stayed None for
    # every candidate. SearchResultItem.explanation is `str` (non-optional), so
    # Pydantic then rejected the whole response with a validation error → 500.
    # Now: use the tolerant parser above, and always fall back to "" instead of None.
    explanations = parse_explanations(raw_explanation, vector_result)

    response_items = []
    for candidate in vector_result:
        name = candidate.get("name", "")
        explanation = explanations.get(name) or "AI explanation temporarily unavailable (quota exceeded). Candidate data is still accurate."

        if not explanation and raw_explanation:
            logger.warning("No explanation parsed for candidate '%s'. Raw Gemini output may have unexpected format.", name)

        item = {
            "id": candidate.get("id"),
            "name": name,
            "email": candidate.get("email"),
            "category": candidate.get("category"),
            "industry": candidate.get("industry"),
            "role": candidate.get("role"),
            "role_en": candidate.get("role_en"),

            # Skills & Experience
            "skills": candidate.get("skills", []),
            "experience_years": candidate.get("experience_years"),

            # Education (nested object)
            "education": candidate.get("education"),
            "additional_education": candidate.get("additional_education", []),

            # Licenses (array of objects)
            "licenses": candidate.get("licenses", []),

            # Location (nested object)
            "location": candidate.get("location"),

            # Languages (array of objects)
            "languages": candidate.get("languages", []),

            # Employment Info
            "salary": candidate.get("salary"),
            "availability": candidate.get("availability"),
            "applicable_tes": candidate.get("applicable_tes"),

            # Summary & Qualification
            "summary": candidate.get("summary"),
            "qualification_issues": candidate.get("qualification_issues", []),

            # Match Score & Explanation
            "match_score": candidate.get("score"),
            "explanation": explanation
        }
        response_items.append(item)

    response_items.sort(
        key=lambda x: (x["experience_years"] or 0, x["match_score"] or 0),
        reverse=True
    )

    top_k = request.top_k or 5
    return {
        "query": request.query,
        "results": response_items[:top_k]
    }
