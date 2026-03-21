from __future__ import annotations

import re
import uuid

from app.db import session_scope
from app.models import AuditLog, CVAnalysis, CVRecord, ResumeScore, ResumeSkill
from app.services.model_loader import get_embed_model, get_ner_model
from app.services.embedding_matcher import extract_required_skills_from_job, match_skills_to_job
from app.services.feedback import generate_feedback_list
from app.services.ner_and_canon import parse_entities
from app.services.scorer import score_components
from app.services.structured_extraction import extract_structured_cv
from app.utils.normalizer import normalize_analysis_result
from app.services.generation import generate_interview_questions, generate_suggestions
from app.utils.pii import strip_pii_for_models


def process_job(job) -> None:
    """
    REFACTORED: No file loading or parsing. CV text comes directly from CVRecord.
    """
    analysis_id = uuid.UUID(job.analysis_id)
    record_id = uuid.UUID(job.resume_id)  # Keep name for backward compatibility

    with session_scope() as db:
        record = db.get(CVRecord, record_id)
        analysis = db.get(CVAnalysis, analysis_id)
        
        if not record or not analysis:
            return
        
        _audit(db, "cv_analyses", analysis.id, "analysis_started", None, {"record_id": str(record.id)})
        
        # *** KEY CHANGE: Use cv_text directly from record ***
        resume_text = record.cv_text
        record.status = "processing"
        db.add(record)
        db.flush()

    m = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", resume_text or "", re.IGNORECASE)
    contact_email = m.group(0) if m else None
    m = re.search(r"\b\+?\d[\d\s().-]{7,}\d\b", resume_text or "")
    contact_phone = re.sub(r"\s+", " ", m.group(0)).strip() if m else None
    m = re.search(r"https?://(?:www\.)?linkedin\.com/[^\s)>,]+", resume_text or "", re.IGNORECASE)
    contact_linkedin = m.group(0).rstrip(".,;") if m else None
    if not contact_linkedin:
        m = re.search(r"\blinkedin\.com/[^\s)>,]+", resume_text or "", re.IGNORECASE)
        contact_linkedin = ("https://" + m.group(0).rstrip(".,;")) if m else None
    m = re.search(r"https?://(?:www\.)?github\.com/[^\s)>,]+", resume_text or "", re.IGNORECASE)
    contact_github = m.group(0).rstrip(".,;") if m else None
    if not contact_github:
        m = re.search(r"\bgithub\.com/[^\s)>,]+", resume_text or "", re.IGNORECASE)
        contact_github = ("https://" + m.group(0).rstrip(".,;")) if m else None
    m = re.search(r"https?://[^\s)>,]+", resume_text or "", re.IGNORECASE)
    contact_portfolio = m.group(0).rstrip(".,;") if m else None
    if contact_portfolio in (contact_linkedin, contact_github):
        contact_portfolio = None

    safe_text = strip_pii_for_models(resume_text)

    entities = parse_entities(safe_text)
    skill_matches = match_skills_to_job(entities.get("skills", []), job.job_description)

    required = extract_required_skills_from_job(job.job_description)
    matched_set = {m["skill"].lower() for m in skill_matches if m.get("skill")}
    missing = [s for s in required if s.lower() not in matched_set]

    score_payload = score_components(entities, skill_matches, resume_text)
    suggestions = generate_feedback_list(entities, resume_text, score_payload, missing)

    prof_entities = entities.get("professional_details", {}) if isinstance(entities, dict) else {}
    exp_val = prof_entities.get("experience")
    exp_items: list[dict] = exp_val if isinstance(exp_val, list) else []
    exp_text = "\n".join([str(x.get("description") or "").strip() for x in exp_items if isinstance(x, dict) and (x.get("description") or "").strip()])

    # Build structured_data from NER entities (minimal mapping)
    # LLM structured_data may have already populated these fields; NER provides fallback.
    structured_data = {
        "personal_details": {
            "full_name": entities.get("personal_details", {}).get("full_name"),
            "email": contact_email or entities.get("personal_details", {}).get("email"),
            "phone": contact_phone or entities.get("personal_details", {}).get("phone"),
            "address": entities.get("personal_details", {}).get("address"),
            "dob": entities.get("personal_details", {}).get("dob"),
            "linkedin": contact_linkedin or entities.get("personal_details", {}).get("linkedin"),
            "github": contact_github or entities.get("personal_details", {}).get("github"),
            "portfolio": contact_portfolio or entities.get("personal_details", {}).get("portfolio"),
        },
        "education_details": {
            "education": entities.get("education_details", {}).get("education") or [],
            "certifications": entities.get("education_details", {}).get("certifications") or [],
            "languages": entities.get("education_details", {}).get("languages") or [],
        },
        "professional_details": {
            "skills": entities.get("professional_details", {}).get("skills") or [],
            # Backward compatible string field + richer structured list field for autofill UIs
            "experience": exp_text or "",
            "experience_items": exp_items,
            "position": entities.get("professional_details", {}).get("position") or "",
            "previous_companies": entities.get("professional_details", {}).get("previous_companies") or [],
            "bio": entities.get("professional_details", {}).get("bio") or "",
        },
    }

    llm_structured = extract_structured_cv(resume_text)
    if isinstance(llm_structured, dict):
        for k in ("personal_details", "education_details", "professional_details"):
            if isinstance(llm_structured.get(k), dict):
                base = structured_data.get(k)
                if isinstance(base, dict):
                    base.update(llm_structured.get(k) or {})
                else:
                    structured_data[k] = llm_structured.get(k)

    # Simple extraction suggestions (e.g., missing LinkedIn, missing email)
    extraction_suggestions = []
    pd = structured_data.get("personal_details", {}) if isinstance(structured_data, dict) else {}
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
        resume_id=str(record_id),
        overall_score=score_payload.get("overall_score"),
        component_scores=score_payload.get("component_scores"),
        evidence=evidence,
        suggestions=match_suggestions,
        raw_payload={"entities": entities, "skill_matches": skill_matches},
        extraction_metadata={"method": "direct_text", "confidence": None, "pages": None, "has_scanned_content": False},
        structured_data=structured_data,
        extraction_suggestions=extraction_suggestions,
        interview_questions=interview_questions,
    )

    # Persist results
    with session_scope() as db:
        analysis = db.get(CVAnalysis, analysis_id)
        record = db.get(CVRecord, record_id)
        if not record or not analysis:
            return

        analysis.result = normalized
        analysis.overall_score = (normalized.get("match_analysis") or {}).get("overall_score")
        analysis.component_scores = (normalized.get("match_analysis") or {}).get("component_scores")
        analysis.status = "completed"
        db.add(analysis)

        record.status = "completed"
        db.add(record)

        _persist_skills(db, record_id, evidence["matched_skills"])

        rs = ResumeScore(
            resume_id=record_id,
            overall_score=(normalized.get("match_analysis") or {}).get("overall_score"),
            component_scores=(normalized.get("match_analysis") or {}).get("component_scores"),
            explanation={"evidence": evidence, "suggestions": suggestions},
        )
        db.add(rs)

        _audit(db, "cv_analyses", analysis.id, "analysis_completed", None, {"overall_score": (normalized.get("match_analysis") or {}).get("overall_score")})


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
