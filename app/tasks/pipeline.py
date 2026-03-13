from __future__ import annotations

import uuid

from app.db import session_scope
from app.models import AuditLog, CVAnalysis, Resume, ResumeScore, ResumeSkill
from app.services.embedding_matcher import extract_required_skills_from_job, match_skills_to_job
from app.services.feedback import generate_feedback_list
from app.services.ner_and_canon import parse_entities
from app.services.parser import extract_text_and_layout
from app.services.scorer import score_components
from app.utils.normalizer import normalize_analysis_result
from app.services.generation import generate_interview_questions, generate_suggestions
from app.utils.storage import load_file_bytes


def process_job(job) -> None:
    analysis_id = uuid.UUID(job.analysis_id)
    resume_id = uuid.UUID(job.resume_id)

    with session_scope() as db:
        resume = db.get(Resume, resume_id)
        analysis = db.get(CVAnalysis, analysis_id)
        if not resume or not analysis:
            return

        _audit(db, "cv_analyses", analysis.id, "analysis_started", None, {"resume_id": str(resume.id)})

        file_bytes = load_file_bytes(resume.storage_key)
        resume_text, extraction_metadata = extract_text_and_layout(file_bytes, resume.content_type or "application/octet-stream")
        resume.resume_text = resume_text
        resume.status = "processing"
        db.add(resume)
        db.flush()

    # PII strip before model calls
    safe_text = strip_pii_for_models(resume_text)

    entities = parse_entities(safe_text)
    skill_matches = match_skills_to_job(entities.get("skills", []), job.job_description)

    required = extract_required_skills_from_job(job.job_description)
    matched_set = {m["skill"].lower() for m in skill_matches if m.get("skill")}
    missing = [s for s in required if s.lower() not in matched_set]

    score_payload = score_components(entities, skill_matches, resume_text)
    suggestions = generate_feedback_list(entities, resume_text, score_payload, missing)

    # Build structured_data from NER entities (minimal mapping)
    structured_data = {
        "personal_details": {
            "full_name": entities.get("personal_details", {}).get("full_name"),
            "email": entities.get("personal_details", {}).get("email"),
            "phone": entities.get("personal_details", {}).get("phone"),
            "address": entities.get("personal_details", {}).get("address"),
            "dob": entities.get("personal_details", {}).get("dob"),
            "linkedin": entities.get("personal_details", {}).get("linkedin"),
            "github": entities.get("personal_details", {}).get("github"),
            "portfolio": entities.get("personal_details", {}).get("portfolio"),
        },
        "education_details": {
            "education": entities.get("education_details", {}).get("education") or [],
        extraction_metadata=extraction_metadata,
        structured_data=structured_data,
        extraction_suggestions=extraction_suggestions,
            "certifications": entities.get("education_details", {}).get("certifications") or [],
            "languages": entities.get("education_details", {}).get("languages") or [],
        },
        "professional_details": {
            "skills": entities.get("professional_details", {}).get("skills") or [],
            "experience": entities.get("professional_details", {}).get("experience") or "",
            "position": entities.get("professional_details", {}).get("position") or "",
            "previous_companies": entities.get("professional_details", {}).get("previous_companies") or [],
            "bio": entities.get("professional_details", {}).get("bio") or "",
        },
    }

    # Simple extraction suggestions (e.g., missing LinkedIn, missing email)
    extraction_suggestions = []
    pd = entities.get("personal_details", {})
    if not pd.get("linkedin"):
        extraction_suggestions.append("Add a LinkedIn URL to your profile.")
    if not pd.get("email"):
        extraction_suggestions.append("Include a contact email address.")
    if not pd.get("phone"):
        extraction_suggestions.append("Include a contact phone number.")

    # Optional LLM-generated interview questions and suggestions
    interview_questions = generate_interview_questions(resume_text, job.job_description)
    llm_suggestions = generate_suggestions({"overall_score": score_payload.get("overall_score"), "missing_skills": missing})

    evidence = {
        "matched_skills": _build_matched_skill_evidence(skill_matches, resume_text),
        "missing_skills": missing,
        "timeline": entities.get("timeline") or [],
    }

    # Merge static and LLM suggestions
    match_suggestions = suggestions + (llm_suggestions if isinstance(llm_suggestions, list) else [])

    normalized = normalize_analysis_result(
        analysis_id=str(analysis_id),
        resume_id=str(resume_id),
        overall_score=score_payload.get("overall_score"),
        component_scores=score_payload.get("component_scores"),
        evidence=evidence,
        suggestions=match_suggestions,
        raw_payload={"entities": entities, "skill_matches": skill_matches},
        extraction_metadata=extraction_metadata,
        structured_data=structured_data,
        extraction_suggestions=extraction_suggestions,
        interview_questions=interview_questions,
    )

    with session_scope() as db:
        analysis = db.get(CVAnalysis, analysis_id)
        resume = db.get(Resume, resume_id)
        if not resume or not analysis:
            return

        analysis.result = normalized
        analysis.overall_score = normalized["overall_score"]
        analysis.component_scores = normalized["component_scores"]
        analysis.status = "completed"
        db.add(analysis)

        resume.status = "completed"
        db.add(resume)

        _persist_skills(db, resume_id, evidence["matched_skills"])

        rs = ResumeScore(
            resume_id=resume_id,
            overall_score=normalized["overall_score"],
            component_scores=normalized["component_scores"],
            explanation={"evidence": evidence, "suggestions": suggestions},
        )
        db.add(rs)

        _audit(db, "cv_analyses", analysis.id, "analysis_completed", None, {"overall_score": normalized["overall_score"]})


def _build_matched_skill_evidence(skill_matches: list[dict], resume_text: str) -> list[dict]:
    out: list[dict] = []
    text = resume_text or ""
    lower = text.lower()
    for m in skill_matches:
        skill = m.get("skill")
        if not skill:
            continue
        idx = lower.find(str(skill).lower())
        snippet = ""
        if idx >= 0:
            start = max(0, idx - 60)
            end = min(len(text), idx + 120)
            snippet = text[start:end].replace("\n", " ").strip()
        out.append({"skill": skill, "snippet": snippet, "score": m.get("score")})
    return out[:200]


def _persist_skills(db, resume_id: uuid.UUID, matched_skills: list[dict]) -> None:
    for ms in matched_skills[:200]:
        db.add(
            ResumeSkill(
                resume_id=resume_id,
                skill=ms.get("skill"),
                canonical_skill=str(ms.get("skill") or "").lower(),
                match_score=ms.get("score"),
                evidence={"snippet": ms.get("snippet"), "score": ms.get("score")},
            )
        )


def _audit(db, entity_type: str, entity_id, action: str, actor_id, payload: dict) -> None:
    try:
        if getattr(getattr(db, "bind", None), "dialect", None) is not None:
            if (db.bind.dialect.name or "").lower() == "sqlite":
                return
    except Exception:
        return

    try:
        db.add(
            AuditLog(
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                actor_id=actor_id,
                payload=payload,
            )
        )
    except Exception:
        # Best-effort: do not fail analysis if audit logging fails.
        # Important: do NOT rollback the surrounding transaction (would wipe analysis persistence).
        return
