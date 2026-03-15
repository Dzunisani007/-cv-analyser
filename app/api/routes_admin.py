from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_bearer_auth_strict
from app.db import session_scope
from app.models import CVAnalysis, Resume
from app.tasks.job_queue import Job, enqueue
from app.utils.signing import sign_storage_key
from app.utils.storage import delete_file

router = APIRouter(prefix="/admin")


@router.post("/analyses/{analysis_id}/rerun")
def rerun(analysis_id: str, _auth: None = Depends(require_bearer_auth_strict)):
    try:
        aid = uuid.UUID(analysis_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid analysis id")

    with session_scope() as db:
        a = db.get(CVAnalysis, aid)
        if not a or not a.resume_id:
            raise HTTPException(status_code=404, detail="analysis not found")
        a.status = "pending"
        a.result = None
        a.overall_score = None
        a.component_scores = None
        db.add(a)
        db.flush()

        enqueue(Job(analysis_id=str(a.id), resume_id=str(a.resume_id), job_description=None))

        return {"analysis_id": str(a.id), "status": a.status}


@router.delete("/resumes/{resume_id}")
def delete_resume(resume_id: str, _auth: None = Depends(require_bearer_auth_strict)):
    try:
        rid = uuid.UUID(resume_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid resume id")

    with session_scope() as db:
        r = db.get(Resume, rid)
        if not r:
            raise HTTPException(status_code=404, detail="resume not found")

        # best-effort storage cleanup
        delete_file(r.storage_key)

        db.delete(r)
        db.flush()
        return {"resume_id": str(rid), "deleted": True}


@router.post("/resumes/{resume_id}/download-token")
def create_download_token(resume_id: str, _auth: None = Depends(require_bearer_auth_strict)):
    try:
        rid = uuid.UUID(resume_id)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid resume id")

    with session_scope() as db:
        r = db.get(Resume, rid)
        if not r:
            raise HTTPException(status_code=404, detail="resume not found")
        if not r.storage_key:
            raise HTTPException(status_code=422, detail="resume has no storage key")

        token = sign_storage_key(r.storage_key, ttl_seconds=300)
        return {"token": token, "expires_in": 300}
