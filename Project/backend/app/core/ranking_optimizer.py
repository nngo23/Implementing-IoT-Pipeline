from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.feedback import Feedback


def calculate_feedback_score(db: Session, candidate_id: str) -> float:
    """
    Calculate ranking bonus/penalty based on feedback history.
    """

    feedback_stats = (
        db.query(
            Feedback.feedback_type,
            func.count(Feedback.id)
        )
        .filter(Feedback.candidate_id == candidate_id)
        .group_by(Feedback.feedback_type)
        .all()
    )

    bonus = 0.0

    for feedback_type, count in feedback_stats:
        if feedback_type == "up":
            bonus += count * 2.0     # 👍 adds +2 per vote
        elif feedback_type == "down":
            bonus -= count * 3.0     # 👎 subtracts -3 per vote

    return bonus
