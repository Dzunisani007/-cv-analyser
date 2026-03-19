"""Initial migration for refactored CV analyser

Revision ID: 20260319_000005
Revises: 
Create Date: 2026-03-19 13:41:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260319_000005'
down_revision = None  # Standalone migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if cv_records table exists, if not create it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'cv_records' not in inspector.get_table_names():
        # Create new cv_records table
        op.create_table('cv_records',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('cv_text', sa.Text(), nullable=False),
            sa.Column('status', sa.Text(), nullable=False, default='pending'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Check if cv_analyses table exists and needs updating
    if 'cv_analyses' in inspector.get_table_names():
        # Check if record_id column exists
        columns = [c['name'] for c in inspector.get_columns('cv_analyses')]
        
        if 'resume_id' in columns and 'record_id' not in columns:
            # Rename resume_id to record_id
            op.alter_column('cv_analyses', 'resume_id',
                existing_type=sa.UUID(),
                new_column_name='record_id')
            
            # Update foreign key constraint if needed
            try:
                op.drop_constraint('cv_analyses_resume_id_fkey', 'cv_analyses', type_='foreignkey')
                op.create_foreign_key(
                    'cv_analyses_record_id_fkey', 
                    'cv_analyses', 
                    'cv_records', 
                    ['record_id'], 
                    ['id'],
                    ondelete='CASCADE'
                )
            except Exception:
                pass  # Constraint might not exist or already updated
        
        # Add job_description column if it doesn't exist
        if 'job_description' not in columns:
            op.add_column('cv_analyses', sa.Column('job_description', sa.Text(), nullable=True))
    
    # Update alembic version table
    op.execute("INSERT INTO alembic_version (version_num) VALUES ('20260319_000005') ON CONFLICT (version_num) DO UPDATE SET version_num = EXCLUDED.version_num")


def downgrade() -> None:
    # This is a complex migration, downgrade would require careful data migration
    # For now, we'll leave downgrade as a no-op
    pass
