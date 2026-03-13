from pydantic import BaseModel


class UploadResponse(BaseModel):
    analysis_id: str
    resume_id: str
    status: str


class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str
    summary: str | None = None
    match_score: int = 0
    missing_skills: list[str] = []
    finished_at: str | None = None


class MatchedSkillEvidence(BaseModel):
    skill: str
    snippet: str | None = None
    score: float | None = None


class TimelineItem(BaseModel):
    company: str | None = None
    title: str | None = None
    from_: str | None = None
    to: str | None = None


class EvidencePayload(BaseModel):
    matched_skills: list[MatchedSkillEvidence] = []
    missing_skills: list[str] = []
    timeline: list[dict] = []


class SuggestionItem(BaseModel):
    id: str
    text: str
    priority: str


class AnalysisResultResponse(BaseModel):
    analysis_id: str
    resume_id: str
    overall_score: float
    component_scores: dict
    evidence: dict
    suggestions: list[dict]
    raw_payload: dict


class HealthResponse(BaseModel):
    db: dict
    storage: dict
    models: dict
