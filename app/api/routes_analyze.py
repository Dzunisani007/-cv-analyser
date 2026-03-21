from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid

router = APIRouter(prefix="/api/v1", tags=["analyze"])


class AnalyzeRequest(BaseModel):
    """Request payload for CV analysis."""
    cv_text: str = Field(..., min_length=10, description="Raw extracted CV text")
    job_description: Optional[str] = Field(None, description="Job description for scoring")
    industry: Optional[str] = Field(None, description="Industry context (e.g., 'technology', 'finance')")


class AnalyzeResponse(BaseModel):
    """Async response for CV analysis."""
    analysis_id: str
    status: str


@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def analyze_cv(request: AnalyzeRequest):
    """
    Accepts raw CV text and job description, enqueues analysis job.
    Returns analysis_id for polling results.
    """
    from app.db import session_scope
    from app.models import CVRecord, CVAnalysis
    from app.tasks.job_queue import Job, enqueue
    
    if not request.cv_text.strip():
        raise HTTPException(status_code=400, detail="cv_text cannot be empty")
    
    with session_scope() as db:
        # Create CV record
        record = CVRecord(cv_text=request.cv_text, status="pending")
        db.add(record)
        db.flush()
        
        # Create analysis
        analysis = CVAnalysis(
            record_id=record.id,
            job_description=request.job_description,
            status="pending"
        )
        db.add(analysis)
        db.flush()
        
        analysis_id = str(analysis.id)
        record_id = str(record.id)
    
    # Enqueue job
    enqueue(Job(
        analysis_id=analysis_id,
        resume_id=record_id,  # Keep field name for backward compatibility
        job_description=request.job_description
    ))
    
    return AnalyzeResponse(analysis_id=analysis_id, status="pending")


@router.get("/analyze/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis."""
    from app.db import session_scope
    from app.models import CVAnalysis
    
    try:
        analysis_uuid = uuid.UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis_id format")
    
    with session_scope() as db:
        analysis = db.get(CVAnalysis, analysis_uuid)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "analysis_id": str(analysis.id),
            "status": analysis.status,
            "overall_score": analysis.overall_score,
            "finished_at": analysis.finished_at.isoformat() if analysis.finished_at else None,
            "warnings": analysis.warnings,
            "started_at": analysis.started_at.isoformat() if analysis.started_at else None
        }


@router.get("/analyze/{analysis_id}/result")
async def get_analysis_result(analysis_id: str):
    """Get the full analysis result."""
    from app.db import session_scope
    from app.models import CVAnalysis
    from app.utils.normalizer import normalize_analysis_result
    
    try:
        analysis_uuid = uuid.UUID(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis_id format")
    
    with session_scope() as db:
        analysis = db.get(CVAnalysis, analysis_uuid)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if analysis.status != "completed":
            # Return result even if failed, with warnings
            return {
                "analysis_id": str(analysis.id),
                "status": analysis.status,
                "warnings": analysis.warnings,
                "result": normalize_analysis_result(analysis.result)
            }
        
        if not analysis.result:
            raise HTTPException(status_code=500, detail="Analysis result is missing")
        
        return normalize_analysis_result(analysis.result)
