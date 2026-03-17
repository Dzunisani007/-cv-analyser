from __future__ import annotations

import uuid
import sqlalchemy as sa
from sqlalchemy import BigInteger, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Resume(Base):
    __tablename__ = "cv_resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

    analyses: Mapped[list[CVAnalysis]] = relationship(
        "CVAnalysis", back_populates="resume", cascade="all, delete-orphan"
    )


class CVAnalysis(Base):
    __tablename__ = "cv_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), ForeignKey("cv_resumes.id", ondelete="CASCADE"), nullable=False
    )
    result = mapped_column(sa.JSON, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    component_scores = mapped_column(sa.JSON, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    warnings = mapped_column(sa.JSON, nullable=True)
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    started_at = mapped_column(sa.DateTime(timezone=True), nullable=True)
    finished_at = mapped_column(sa.DateTime(timezone=True), nullable=True)

    resume: Mapped[Resume] = relationship("Resume", back_populates="analyses")


class ResumeSkill(Base):
    __tablename__ = "cv_resume_skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), ForeignKey("cv_resumes.id", ondelete="CASCADE"), nullable=False
    )
    skill: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical_skill: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence = mapped_column(sa.JSON, nullable=True)


class ResumeScore(Base):
    __tablename__ = "cv_resume_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), ForeignKey("cv_resumes.id", ondelete="CASCADE"), nullable=False
    )
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    component_scores = mapped_column(sa.JSON, nullable=True)
    explanation = mapped_column(sa.JSON, nullable=True)
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())


class AuditLog(Base):
    __tablename__ = "cv_audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    action: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    payload = mapped_column(sa.JSON, nullable=True)
    ts = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())


class WorkflowAuditLog(Base):
    """Audit log for Risk Gate workflow progression."""
    __tablename__ = "cv_workflow_audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), ForeignKey("cv_analyses.id", ondelete="CASCADE"), nullable=False
    )
    from_stage: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_stage: Mapped[str | None] = mapped_column(Text, nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)  # 'advance', 'reject', 'approve'
    actor_id: Mapped[uuid.UUID | None] = mapped_column(sa.UUID(as_uuid=True), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_assessment = mapped_column(sa.JSON, nullable=True)
    created_at = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())

    analysis: Mapped[CVAnalysis] = relationship("CVAnalysis", back_populates="workflow_logs")
