from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth import require_bearer_auth
from app.config import settings
from app.db import session_scope
from app.models import CVAnalysis, Resume
from app.tasks.job_queue import Job, enqueue
from app.utils.storage import save_file

router = APIRouter()


@router.post("/upload", status_code=202)
async def upload_resume(
    file: UploadFile = File(...),
    uploaded_by: str | None = Form(None),
    job_description: str | None = Form(None),
    _auth: None = Depends(require_bearer_auth),
):
    allowed = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "image/png",
        "image/jpeg",
    }
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="unsupported file type")

    file_bytes = await file.read()
    if len(file_bytes) > int(settings.max_upload_mb) * 1024 * 1024:
        raise HTTPException(status_code=413, detail="file too large")

    storage = save_file(file_bytes, file.filename, file.content_type)

    uploaded_by_uuid: uuid.UUID | None = None
    if uploaded_by:
        uploaded_by_uuid = uuid.UUID(uploaded_by)

    analysis_id: str | None = None
    resume_db_id: str | None = None

    with session_scope() as db:
        resume = Resume(
            uploaded_by=uploaded_by_uuid,
            filename=file.filename,
            storage_key=storage["storage_key"],
            content_type=file.content_type,
            size_bytes=storage["size_bytes"],
            resume_text=None,
            status="pending",
        )
        db.add(resume)
        db.flush()

        analysis = CVAnalysis(
            resume_id=resume.id,
            status="pending",
            result=None,
            overall_score=None,
            component_scores=None,
            warnings=None,
        )
        db.add(analysis)
        db.flush()

        # capture ids; session_scope will commit on exit
        analysis_id = str(analysis.id)
        resume_db_id = str(resume.id)

    # Enqueue only after commit so the job can see the analysis row immediately (INLINE_JOBS tests).
    enqueue(Job(analysis_id=analysis_id, resume_id=resume_db_id, job_description=job_description))

    return {
        "analysis_id": analysis_id,
        "resume_id": resume_db_id,
        "status": "pending",
    }
