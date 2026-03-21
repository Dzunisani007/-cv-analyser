"""Initialize analyser database with clean tables

Revision ID: 20260321_init_analyser_clean
Revises: 
Create Date: 2026-03-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260321_init_analyser_clean'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    
    # Create cv_records table
    op.create_table('cv_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('cv_text', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    
    # Create cv_analyses table
    op.create_table('cv_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('record_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cv_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('component_scores', sa.JSON(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False, default='pending'),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create cv_resume_skills table
    op.create_table('cv_resume_skills',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cv_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill', sa.Text(), nullable=True),
        sa.Column('canonical_skill', sa.Text(), nullable=True),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
    )
    
    # Create cv_resume_scores table
    op.create_table('cv_resume_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cv_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('component_scores', sa.JSON(), nullable=True),
        sa.Column('explanation', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    
    # Create cv_audit_logs table
    op.create_table('cv_audit_logs',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('entity_type', sa.Text(), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('ts', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    
    # Create cv_workflow_audit_logs table
    op.create_table('cv_workflow_audit_logs',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cv_analyses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_stage', sa.Text(), nullable=True),
        sa.Column('to_stage', sa.Text(), nullable=True),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('risk_assessment', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    
    # Update alembic version
    op.execute("INSERT INTO alembic_version (version_num) VALUES ('20260321_init_analyser_clean') ON CONFLICT (version_num) DO UPDATE SET version_num = EXCLUDED.version_num")


def downgrade() -> None:
    op.drop_table('cv_workflow_audit_logs')
    op.drop_table('cv_audit_logs')
    op.drop_table('cv_resume_scores')
    op.drop_table('cv_resume_skills')
    op.drop_table('cv_analyses')
    op.drop_table('cv_records')
