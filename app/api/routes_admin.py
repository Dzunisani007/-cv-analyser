from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_bearer_auth_strict
from app.db import session_scope
from app.models import CVAnalysis, CVRecord
from app.tasks.job_queue import Job, enqueue

router = APIRouter(prefix="/admin")


@router.post("/analyses/{analysis_id}/rerun")
def rerun(analysis_id: str, _auth: None = Depends(require_bearer_auth_strict)):
    try:
        aid = uuid.UUID(analysis_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid analysis id")

    with session_scope() as db:
        a = db.get(CVAnalysis, aid)
        if not a or not a.record_id:
            raise HTTPException(status_code=404, detail="analysis not found")
        a.status = "pending"
        a.result = None
        a.overall_score = None
        a.component_scores = None
        db.add(a)
        db.flush()

        enqueue(Job(analysis_id=str(a.id), resume_id=str(a.record_id), job_description=None))

        return {"analysis_id": str(a.id), "status": a.status}


@router.delete("/records/{record_id}")
def delete_record(record_id: str, _auth: None = Depends(require_bearer_auth_strict)):
    try:
        rid = uuid.UUID(record_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid record id")

    with session_scope() as db:
        r = db.get(CVRecord, rid)
        if not r:
            raise HTTPException(status_code=404, detail="record not found")

        db.delete(r)
        db.flush()
        return {"record_id": str(rid), "deleted": True}


