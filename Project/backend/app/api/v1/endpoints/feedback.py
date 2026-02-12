from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.feedback import Feedback
from app.utils.feedback_tags import generate_auto_tags
from sqlalchemy import func

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/feedback")
def save_feedback(data: dict, db: Session = Depends(get_db)):
    auto_tags = generate_auto_tags(data.get("reason", ""))

    feedback = Feedback(
        candidate_id=data.get("candidate_id"),
        feedback_type=data.get("feedback_type"),
        reason=data.get("reason"),
        auto_tags=auto_tags
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return {"message": "Feedback saved", "auto_tags": auto_tags}

@router.get("/feedback/stats")
def feedback_stats(db: Session = Depends(get_db)):
    results = (
        db.query(Feedback.auto_tags, func.count(Feedback.id))
        .group_by(Feedback.auto_tags)
        .all()
    )

    return results