from __future__ import annotations


def generate_feedback_list(entities: dict, resume_text: str, score_payload: dict, missing_skills: list[str]) -> list[dict]:
    suggestions: list[dict] = []

    cs = (score_payload or {}).get("component_scores") or {}
    if float(cs.get("skills") or 0.0) < 0.5:
        suggestions.append(
            {
                "id": "add_skills",
                "text": "Add more job-relevant skills and include them in bullet points.",
                "priority": "high",
            }
        )

    if missing_skills:
        suggestions.append(
            {
                "id": "missing_skills",
                "text": "Consider adding these skills if you have experience: " + ", ".join(missing_skills[:12]),
                "priority": "high" if len(missing_skills) <= 6 else "medium",
            }
        )

    if float(cs.get("format") or 0.0) < 0.6:
        suggestions.append(
            {
                "id": "formatting",
                "text": "Use bullet points and quantify achievements with numbers (%, $, time saved).",
                "priority": "medium",
            }
        )

    if float(cs.get("experience") or 0.0) < 0.5:
        suggestions.append(
            {
                "id": "experience",
                "text": "Add clearer dates and scope for each role (team size, impact, technologies).",
                "priority": "medium",
            }
        )

    return suggestions
