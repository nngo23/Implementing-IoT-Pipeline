from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
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
async def search_candidates(request: SearchRequest, db: Session = Depends(get_db)):
    try:
        # Step 1: vector search
        vector_result = vector_search.search_similar(
            request.query, top_k=request.top_k,
            industry=request.industry,
            salary_range=request.salary_range,
            location_filter=request.location_filter
        )
        if not vector_result:
            raise HTTPException(status_code=404, detail="No candidates found")

        # Step 2: adjusted scoring
        adjusted = []
        for c in vector_result:
            base = c.get("score", 0)
            bonus = calculate_feedback_score(db, c.get("id"))
            c["adjusted_score"] = base + bonus
            adjusted.append(c)
        adjusted.sort(key=lambda x: x["adjusted_score"], reverse=True)

        # Step 3: build prompt adjustment
        feedback_adjustment = build_feedback_prompt_adjustment(db)
        optimized_query = request.query + "\n" + feedback_adjustment

        # Step 4: Gemini explanation
        explanation = gemini_client.generate_text(optimized_query, adjusted) or ""

        # Step 5: build response
        items = []
        for c in adjusted:
            expl_text = ""
            # parse explanations by candidate
            if explanation:
                parts = explanation.split("**")
                for i in range(1, len(parts), 2):
                    name = parts[i].strip()
                    text = parts[i+1].strip() if (i+1) < len(parts) else ""
                    if name == c.get("name"):
                        expl_text = text
                        break

            items.append({
                "id": c.get("id"),
                "name": c.get("name"),
                "category": c.get("category"),
                "industry": c.get("industry"),
                "role": c.get("role"),
                "role_en": c.get("role_en"),
                "skills": c.get("skills", []),
                "experience_years": c.get("experience_years"),
                "education": c.get("education"),
                "additional_education": c.get("additional_education", []),
                "licenses": c.get("licenses", []),
                "location": c.get("location"),
                "languages": c.get("languages", []),
                "salary": c.get("salary"),
                "availability": c.get("availability"),
                "applicable_tes": c.get("applicable_tes"),
                "summary": c.get("summary"),
                "qualification_issues": c.get("qualification_issues", []),
                "match_score": round(c.get("adjusted_score", 0), 2),
                # always string ("" fallback)
                "explanation": expl_text or ""
            })
        return {"query": request.query, "results": items}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
