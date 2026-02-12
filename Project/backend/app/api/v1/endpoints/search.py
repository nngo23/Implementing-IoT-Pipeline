from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict
from app.schemas.search import SearchRequest, SearchResponse
from app.core.vector_search import vector_search
from app.core.gemini import gemini_client
from app.db.database import SessionLocal
from app.core.feedback_optimizer import build_feedback_prompt_adjustment
from app.core.ranking_optimizer import calculate_feedback_score

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_candidates(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    try:

        # ---------------------------------
        # 1️⃣ Build Feedback Weights
        # ---------------------------------
        feedback_weights: Dict[str, float] = {}

        # Get broad set first
        initial_candidates = vector_search.search_similar(
            request.query,
            top_k=100,
            industry=request.industry,
            salary_range=request.salary_range,
            location_filter=request.location_filter
        )

        for candidate in initial_candidates:
            candidate_id = candidate.get("id")
            bonus = calculate_feedback_score(db, candidate_id)
            feedback_weights[candidate_id] = 1 + bonus

        # ---------------------------------
        # 2️⃣ Final Vector Search (Weighted)
        # ---------------------------------
        vector_result = vector_search.search_similar(
            request.query,
            top_k=request.top_k,
            industry=request.industry,
            salary_range=request.salary_range,
            location_filter=request.location_filter,
            feedback_weights=feedback_weights
        )

        if not vector_result:
            raise HTTPException(status_code=404, detail="No candidates found")

        # ---------------------------------
        # 3️⃣ Gemini Explanation
        # ---------------------------------
        feedback_adjustment = build_feedback_prompt_adjustment(db)
        optimized_query = request.query + "\n" + feedback_adjustment

        try:
            explanation = gemini_client.generate_text(
                optimized_query,
                vector_result
            ) or ""
        except Exception:
            explanation = ""

        # ---------------------------------
        # 4️⃣ Build Response
        # ---------------------------------
        items = []

        for candidate in vector_result:

            explanation_text = ""

            if explanation:
                parts = explanation.split("**")
                for i in range(1, len(parts), 2):
                    name = parts[i].strip()
                    text = parts[i + 1].strip() if (i + 1) < len(parts) else ""
                    if name == candidate.get("name"):
                        explanation_text = text
                        break

            items.append({
                "id": candidate.get("id"),
                "name": candidate.get("name"),
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
                "explanation": explanation_text
            })

        return {
            "query": request.query,
            "results": items
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
