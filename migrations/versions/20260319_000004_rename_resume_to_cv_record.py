"""Rename resume to cv_record and update schema

Revision ID: 20260319_000004
Revises: 20260317_approval
Create Date: 2026-03-19 10:19:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260319_000004'
down_revision = '20260317_approval'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create new cv_records table
    op.create_table('cv_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('cv_text', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate data from cv_resumes to cv_records
    op.execute("""
        INSERT INTO cv_records (id, cv_text, status, created_at, updated_at)
        SELECT id, resume_text, status, created_at, updated_at
        FROM cv_resumes
        WHERE resume_text IS NOT NULL
    """)
    
    # Update cv_analyses to reference cv_records
    op.alter_column('cv_analyses', 'resume_id',
        existing_type=sa.UUID(),
        new_column_name='record_id')
    
    # Drop and recreate foreign key constraint
    op.drop_constraint('cv_analyses_resume_id_fkey', 'cv_analyses', type_='foreignkey')
    op.create_foreign_key(
        'cv_analyses_record_id_fkey', 
        'cv_analyses', 
        'cv_records', 
        ['record_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    # Add job_description column to cv_analyses
    op.add_column('cv_analyses', sa.Column('job_description', sa.Text(), nullable=True))
    
    # Update other tables that reference cv_resumes
    op.drop_constraint('cv_resume_skills_resume_id_fkey', 'cv_resume_skills', type_='foreignkey')
    op.create_foreign_key(
        'cv_resume_skills_resume_id_fkey', 
        'cv_resume_skills', 
        'cv_records', 
        ['resume_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    op.drop_constraint('cv_resume_scores_resume_id_fkey', 'cv_resume_scores', type_='foreignkey')
    op.create_foreign_key(
        'cv_resume_scores_resume_id_fkey', 
        'cv_resume_scores', 
        'cv_records', 
        ['resume_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    # Drop the old cv_resumes table
    op.drop_table('cv_resumes')


def downgrade() -> None:
    # Recreate cv_resumes table with old structure
    op.create_table('cv_resumes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('uploaded_by', sa.UUID(), nullable=True),
        sa.Column('filename', sa.Text(), nullable=True),
        sa.Column('storage_key', sa.Text(), nullable=True),
        sa.Column('content_type', sa.Text(), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate data back
    op.execute("""
        INSERT INTO cv_resumes (id, resume_text, status, created_at, updated_at)
        SELECT id, cv_text, status, created_at, updated_at
        FROM cv_records
    """)
    
    # Update foreign keys back
    op.alter_column('cv_analyses', 'record_id',
        existing_type=sa.UUID(),
        new_column_name='resume_id')
    
    op.drop_constraint('cv_analyses_record_id_fkey', 'cv_analyses', type_='foreignkey')
    op.create_foreign_key(
        'cv_analyses_resume_id_fkey', 
        'cv_analyses', 
        'cv_resumes', 
        ['resume_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    # Drop job_description column
    op.drop_column('cv_analyses', 'job_description')
    
    # Update other tables
    op.drop_constraint('cv_resume_skills_resume_id_fkey', 'cv_resume_skills', type_='foreignkey')
    op.create_foreign_key(
        'cv_resume_skills_resume_id_fkey', 
        'cv_resume_skills', 
        'cv_resumes', 
        ['resume_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    op.drop_constraint('cv_resume_scores_resume_id_fkey', 'cv_resume_scores', type_='foreignkey')
    op.create_foreign_key(
        'cv_resume_scores_resume_id_fkey', 
        'cv_resume_scores', 
        'cv_resumes', 
        ['resume_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    # Drop cv_records table
    op.drop_table('cv_records')
