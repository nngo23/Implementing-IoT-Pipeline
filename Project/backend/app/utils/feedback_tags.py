def generate_auto_tags(reason: str):
    tags = []

    reason = (reason or "").lower()

    if "salary" in reason:
        tags.append("salary")
    if "skill" in reason or "experience" in reason:
        tags.append("skills")
    if "distance" in reason or "location" in reason:
        tags.append("distance")
    if "certificate" in reason or "iso" in reason:
        tags.append("certification")
    if "education" in reason:
        tags.append("education")

    return tags
