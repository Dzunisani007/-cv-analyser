"""Debug version of analyze endpoint to isolate the issue"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import traceback

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


@router.post("/analyze-debug", response_model=AnalyzeResponse, status_code=202)
async def analyze_cv_debug(request: AnalyzeRequest):
    """
    Debug version of CV analysis endpoint with detailed error logging.
    """
    try:
        print("Starting analyze_cv_debug...")
        
        if not request.cv_text.strip():
            raise HTTPException(status_code=400, detail="cv_text cannot be empty")
        
        print("CV text validation passed")
        
        # Test database import
        try:
            from app.db import session_scope
            print("session_scope imported successfully")
        except Exception as e:
            print(f"Failed to import session_scope: {e}")
            raise HTTPException(status_code=500, detail=f"Database import error: {e}")
        
        # Test model imports
        try:
            from app.models import CVRecord, CVAnalysis
            print("Models imported successfully")
        except Exception as e:
            print(f"Failed to import models: {e}")
            raise HTTPException(status_code=500, detail=f"Model import error: {e}")
        
        # Test job queue import
        try:
            from app.tasks.job_queue import Job, enqueue
            print("Job queue imported successfully")
        except Exception as e:
            print(f"Failed to import job queue: {e}")
            raise HTTPException(status_code=500, detail=f"Job queue import error: {e}")
        
        # Test database session
        try:
            with session_scope() as db:
                print("Database session created successfully")
                
                # Create CV record
                record = CVRecord(cv_text=request.cv_text, status="pending")
                db.add(record)
                db.flush()
                print(f"CVRecord created with ID: {record.id}")
                
                # Create analysis
                analysis = CVAnalysis(
                    record_id=record.id,
                    job_description=request.job_description,
                    status="pending"
                )
                db.add(analysis)
                db.flush()
                print(f"CVAnalysis created with ID: {analysis.id}")
                
                analysis_id = str(analysis.id)
                record_id = str(record.id)
                
        except Exception as e:
            print(f"Database operation failed: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        
        # Test job enqueue
        try:
            enqueue(Job(
                analysis_id=analysis_id,
                resume_id=record_id,
                job_description=request.job_description
            ))
            print("Job enqueued successfully")
        except Exception as e:
            print(f"Job enqueue failed: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Job queue error: {e}")
        
        print("analyze_cv_debug completed successfully")
        return AnalyzeResponse(analysis_id=analysis_id, status="pending")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
