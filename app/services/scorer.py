from __future__ import annotations

import re
from typing import Dict, Any, Optional

from .structural_validator import StructuralValidator
from .risk_assessor import CVRiskAssessor


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


def score_components(entities: dict, skill_matches: list[dict], resume_text: str,
                    structured_data: Optional[Dict[str, Any]] = None,
                    job_requirements: Optional[Dict[str, Any]] = None,
                    industry: Optional[str] = None) -> dict:
    # Original scoring logic
    skill_score = compute_skill_score(skill_matches)
    experience_score = _experience_score_from_text(resume_text)
    education_score = _education_score_from_text(resume_text)
    format_score = _format_score_from_text(resume_text)

    # Calculate base component scores
    component_scores = {
        "skills": float(_clamp01(skill_score)),
        "experience": float(_clamp01(experience_score)),
        "education": float(_clamp01(education_score)),
        "format": float(_clamp01(format_score)),
    }

    # Initialize enhanced results
    structural_validation = None
    risk_assessment = None
    enhanced_overall_score = None

    # Add Risk Gate enhancements if structured data is available
    if structured_data:
        # Structural validation
        validator = StructuralValidator()
        structural_validation = validator.validate_cv_structure(
            structured_data,
            industry
        )

        # Risk assessment
        if job_requirements:
            assessor = CVRiskAssessor()
            risk_assessment = assessor.assess_cv_risks(
                {
                    'structured_data': structured_data,
                    'extraction_metadata': {},
                    'match_analysis': {
                        'overall_score': 0,  # Will be calculated below
                        'component_scores': component_scores
                    }
                },
                job_requirements,
                industry
            )

            # Adjust overall score based on risk assessment
            risk_penalty = max(0, (100 - risk_assessment.overall_score) / 100) * 0.3  # Max 30% penalty
            # enhanced_overall_score is computed after base overall is calculated
            enhanced_overall_score = 1.0 - risk_penalty
        else:
            # Fallback risk assessment without job requirements
            assessor = CVRiskAssessor()
            risk_assessment = assessor.assess_cv_risks(
                {
                    'structured_data': structured_data,
                    'extraction_metadata': {},
                    'match_analysis': {
                        'overall_score': 0,
                        'component_scores': component_scores
                    }
                },
                {},
                industry
            )

    # Calculate original overall score
    weights = {"skills": 0.5, "experience": 0.3, "education": 0.1, "format": 0.1}
    overall = (
        skill_score * weights["skills"]
        + experience_score * weights["experience"]
        + education_score * weights["education"]
        + format_score * weights["format"]
    )

    base_overall_pct = float(_clamp01(overall) * 100.0)

    result = {
        "overall_score": base_overall_pct,
        "component_scores": component_scores
    }

    # Add enhanced features if available
    if structural_validation:
        result["structural_validation"] = {
            "completeness_score": structural_validation.completeness_score,
            "is_complete": structural_validation.is_complete,
            "critical_issues": [issue.message for issue in structural_validation.critical_issues],
            "warnings": [issue.message for issue in structural_validation.warnings],
            "suggestions": [issue.message for issue in structural_validation.suggestions],
            "compliance_score": structural_validation.compliance_score,
            "industry_compliance": structural_validation.industry_compliance
        }

    if risk_assessment:
        result["risk_assessment"] = {
            "overall_score": risk_assessment.overall_score,
            "risk_level": risk_assessment.risk_level.value,
            "critical_issues": risk_assessment.critical_issues,
            "warnings": risk_assessment.warnings,
            "recommendations": risk_assessment.recommendations,
            "compliance_status": {k: v.value for k, v in risk_assessment.compliance_status.items()},
            "industry_score": risk_assessment.industry_score,
            "completeness_score": risk_assessment.completeness_score
        }

        # Use enhanced score if risk assessment is available
        if enhanced_overall_score is not None:
            # In job_requirements mode enhanced_overall_score stores the multiplicative factor
            if 0.0 <= float(enhanced_overall_score) <= 1.0:
                result["overall_score"] = float(base_overall_pct * float(enhanced_overall_score))

    return result
