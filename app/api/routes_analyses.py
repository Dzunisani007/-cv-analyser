from __future__ import annotations

import uuid

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from app.auth import require_bearer_auth
from app.db import session_scope
from app.utils.normalizer import _adapt_legacy_result

from app.models import CVAnalysis


router = APIRouter()


@router.get("/analyses/{analysis_id}/status")
def get_status(analysis_id: str, _auth: None = Depends(require_bearer_auth)):
    try:
        aid = uuid.UUID(analysis_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid analysis id")

    with session_scope() as db:
        a = db.get(CVAnalysis, aid)
        if not a:
            raise HTTPException(status_code=404, detail="analysis not found")

        result = a.result or {}
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                result = {}
        # Ensure v1 shape for UI
        result = _adapt_legacy_result(result)

        match_analysis = result.get("match_analysis", {})
        evidence = match_analysis.get("evidence", {})
        missing = evidence.get("missing_skills", [])
        overall = match_analysis.get("overall_score", 0.0)

        return {
            "analysis_id": str(a.id),
            "status": a.status,
            "summary": None,
            "match_score": int(float(overall)),
            "missing_skills": missing,
            "finished_at": getattr(a, "finished_at", None),
            "warnings": a.warnings,
        }


@router.get("/analyses/{analysis_id}/result")
def get_result(analysis_id: str, _auth: None = Depends(require_bearer_auth)):
    try:
        aid = uuid.UUID(analysis_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid analysis id")

    with session_scope() as db:
        a = db.get(CVAnalysis, aid)
        if not a:
            raise HTTPException(status_code=404, detail="analysis not found")
        if a.status != "completed":
            raise HTTPException(status_code=409, detail="analysis not completed")
        if not a.result:
            raise HTTPException(status_code=500, detail="missing result")

        payload = a.result
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                raise HTTPException(status_code=500, detail="invalid stored result")

        # Ensure v1 shape for UI
        payload = _adapt_legacy_result(payload)

        # Backward compatibility: promote match_analysis fields to top-level for existing tests/UIs
        match_analysis = payload.get("match_analysis", {})
        if "overall_score" in match_analysis:
            payload["overall_score"] = match_analysis["overall_score"]
        if "component_scores" in match_analysis:
            payload["component_scores"] = match_analysis["component_scores"]
        if "evidence" in match_analysis:
            payload["evidence"] = match_analysis["evidence"]
        if "match_suggestions" in match_analysis:
            payload["suggestions"] = match_analysis["match_suggestions"]
        # Keep raw_payload as-is for test expectations

        return jsonable_encoder(payload)
