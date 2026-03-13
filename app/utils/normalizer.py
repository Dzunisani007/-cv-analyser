from __future__ import annotations


def normalize_analysis_result(
    *,
    analysis_id: str,
    resume_id: str,
    overall_score: float | None,
    component_scores: dict | None,
    evidence: dict | None,
    suggestions: list[dict] | None,
    raw_payload: dict | None,
    extraction_metadata: dict | None = None,
    structured_data: dict | None = None,
    extraction_suggestions: list[str] | None = None,
    interview_questions: list[str] | None = None,
) -> dict:
    return {
        "schema_version": "v1",
        "extraction_metadata": extraction_metadata
        or {
            "method": "unknown",
            "confidence": None,
            "pages": None,
            "has_scanned_content": False,
        },
        "structured_data": structured_data
        or {
            "personal_details": {},
            "education_details": {"education": [], "certifications": [], "languages": []},
            "professional_details": {"skills": [], "experience": "", "position": "", "previous_companies": [], "bio": ""},
        },
        "match_analysis": {
            "overall_score": float(overall_score or 0.0),
            "component_scores": component_scores
            or {"skills": 0.0, "experience": 0.0, "education": 0.0, "format": 0.0},
            "evidence": evidence
            or {"matched_skills": [], "missing_skills": [], "timeline": []},
            "match_suggestions": suintrviw_qustionso [],
            "interview_questions": [],  # placeholder; can be added later
        },
        "extraction_suggestions": extraction_suggestions or [],
        "raw_payload": raw_payload or {},
    }


def _adapt_legacy_result(result: dict) -> dict:
    """If a result lacks schema_version, adapt old shape to v1 for API responses."""
    if result.get("schema_version") == "v1":
        return result

    # Old shape: {analysis_id, resume_id, overall_score, component_scores, evidence, suggestions, raw_payload}
    return {
        "schema_version": "v1",
        "extraction_metadata": {"method": "unknown", "confidence": None, "pages": None, "has_scanned_content": False},
        "structured_data": {
            "personal_details": {},
            "education_details": {"education": [], "certifications": [], "languages": []},
            "professional_details": {"skills": [], "experience": "", "position": "", "previous_companies": [], "bio": ""},
        },
        "match_analysis": {
            "overall_score": float(result.get("overall_score", 0.0)),
            "component_scores": result.get("component_scores") or {"skills": 0.0, "experience": 0.0, "education": 0.0, "format": 0.0},
            "evidence": result.get("evidence") or {"matched_skills": [], "missing_skills": [], "timeline": []},
            "match_suggestions": result.get("suggestions") or [],
            "interview_questions": [],
        },
        "extraction_suggestions": [],
        "raw_payload": result.get("raw_payload") or {},
    }
