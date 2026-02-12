from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.feedback import Feedback


def build_feedback_prompt_adjustment(db: Session) -> str:
    """
    Analyze negative feedback trends and adjust prompt emphasis.
    Lightweight RLHF-style optimization.
    """

    stats = (
        db.query(Feedback.auto_tags, func.count(Feedback.id))
        .filter(Feedback.feedback_type == "down")
        .group_by(Feedback.auto_tags)
        .all()
    )

    emphasis_rules = []

    for tags, count in stats:
        if not tags:
            continue

        if "salary" in tags:
            emphasis_rules.append("Strongly prioritize salary match.")
        if "skills" in tags:
            emphasis_rules.append("Strongly emphasize required skills and certifications.")
        if "distance" in tags:
            emphasis_rules.append("Prioritize candidates closer to company location.")
        if "certification" in tags:
            emphasis_rules.append("Ensure required certifications are strictly matched.")
        if "education" in tags:
            emphasis_rules.append("Pay attention to education level requirements.")

    if not emphasis_rules:
        return ""

    return "\nIMPORTANT OPTIMIZATION RULES BASED ON USER FEEDBACK:\n" + "\n".join(set(emphasis_rules))
