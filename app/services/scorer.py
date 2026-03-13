from __future__ import annotations

import re


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def compute_skill_score(skill_matches: list[dict], required_count: int = 0) -> float:
    if not skill_matches:
        return 0.0

    scored = [m for m in skill_matches if m.get("score") is not None]
    if not scored:
        return _clamp01(len(skill_matches) / 20.0)

    matched = [m for m in scored if float(m.get("score") or 0.0) >= 0.7]
    if required_count > 0:
        return _clamp01(len(matched) / float(required_count))
    return _clamp01(len(matched) / float(max(1, len(scored))))


def _experience_score_from_text(resume_text: str) -> float:
    t = resume_text.lower()
    if "years" in t:
        return 0.7
    if re.search(r"\b20\d{2}\b", t):
        return 0.5
    return 0.3


def _education_score_from_text(resume_text: str) -> float:
    t = resume_text.lower()
    if any(k in t for k in ["phd", "doctorate"]):
        return 0.9
    if any(k in t for k in ["master", "msc", "m.sc", "mba"]):
        return 0.75
    if any(k in t for k in ["bachelor", "bsc", "b.sc", "ba", "bs"]):
        return 0.6
    return 0.3


def _format_score_from_text(resume_text: str) -> float:
    lines = [l for l in (resume_text or "").splitlines() if l.strip()]
    if len(lines) < 5:
        return 0.4
    if any(l.strip().startswith(("-", "*")) for l in lines):
        return 0.8
    return 0.6


def score_components(entities: dict, skill_matches: list[dict], resume_text: str) -> dict:
    skill_score = compute_skill_score(skill_matches)
    experience_score = _experience_score_from_text(resume_text)
    education_score = _education_score_from_text(resume_text)
    format_score = _format_score_from_text(resume_text)

    weights = {"skills": 0.5, "experience": 0.3, "education": 0.1, "format": 0.1}
    overall = (
        skill_score * weights["skills"]
        + experience_score * weights["experience"]
        + education_score * weights["education"]
        + format_score * weights["format"]
    )
    component_scores = {
        "skills": float(_clamp01(skill_score)),
        "experience": float(_clamp01(experience_score)),
        "education": float(_clamp01(education_score)),
        "format": float(_clamp01(format_score)),
    }
    return {"overall_score": float(_clamp01(overall) * 100.0), "component_scores": component_scores}
