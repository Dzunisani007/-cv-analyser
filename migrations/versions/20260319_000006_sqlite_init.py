"""SQLite migration for refactored CV analyser

Revision ID: 20260319_000006
Revises: 
Create Date: 2026-03-19 13:41:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260319_000006'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create cv_records table
    op.create_table('cv_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('cv_text', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create cv_analyses table
    op.create_table('cv_analyses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('record_id', sa.UUID(), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('component_scores', sa.JSON(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False, default='pending'),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['record_id'], ['cv_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create supporting tables
    op.create_table('cv_resume_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.UUID(), nullable=False),
        sa.Column('skill', sa.Text(), nullable=True),
        sa.Column('canonical_skill', sa.Text(), nullable=True),
        sa.Column('match_score', sa.Float(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['resume_id'], ['cv_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('cv_resume_scores',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('resume_id', sa.UUID(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('component_scores', sa.JSON(), nullable=True),
        sa.Column('explanation', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['resume_id'], ['cv_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Update alembic version
    op.execute("INSERT OR REPLACE INTO alembic_version (version_num) VALUES ('20260319_000006')")


def downgrade() -> None:
    op.drop_table('alembic_version')
    op.drop_table('cv_resume_scores')
    op.drop_table('cv_resume_skills')
    op.drop_table('cv_analyses')
    op.drop_table('cv_records')
