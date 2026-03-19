"""Production migration for refactored CV analyser

Revision ID: 20260319_000007
Revises: 20260317_approval
Create Date: 2026-03-19 13:59:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260319_000007'
down_revision = '20260317_approval'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if cv_records table exists, if not create it
    tables = inspector.get_table_names()
    
    if 'cv_records' not in tables:
        # Create cv_records table
        op.create_table('cv_records',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('cv_text', sa.Text(), nullable=False),
            sa.Column('status', sa.Text(), nullable=False, default='pending'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        print("✅ Created cv_records table")
    else:
        print("✅ cv_records table already exists")
    
    # Update cv_analyses table if needed
    if 'cv_analyses' in tables:
        columns = [c['name'] for c in inspector.get_columns('cv_analyses')]
        
        # Rename resume_id to record_id if needed
        if 'resume_id' in columns and 'record_id' not in columns:
            op.alter_column('cv_analyses', 'resume_id',
                existing_type=sa.UUID(),
                new_column_name='record_id')
            print("✅ Renamed resume_id to record_id")
        
        # Add job_description if missing
        if 'job_description' not in columns:
            op.add_column('cv_analyses', sa.Column('job_description', sa.Text(), nullable=True))
            print("✅ Added job_description column")
        
        # Update foreign key constraint
        try:
            # Drop old constraint if it exists
            op.drop_constraint('cv_analyses_resume_id_fkey', 'cv_analyses', type_='foreignkey')
            # Create new constraint
            op.create_foreign_key(
                'cv_analyses_record_id_fkey', 
                'cv_analyses', 
                'cv_records', 
                ['record_id'], 
                ['id'],
                ondelete='CASCADE'
            )
            print("✅ Updated foreign key constraint")
        except Exception:
            print("⚠️ Could not update foreign key constraint (might not exist)")
    
    # Update other tables' foreign keys if needed
    for table_name in ['cv_resume_skills', 'cv_resume_scores']:
        if table_name in tables:
            try:
                op.drop_constraint(f'{table_name}_resume_id_fkey', table_name, type_='foreignkey')
                op.create_foreign_key(
                    f'{table_name}_resume_id_fkey', 
                    table_name, 
                    'cv_records', 
                    ['resume_id'], 
                    ['id'],
                    ondelete='CASCADE'
                )
                print(f"✅ Updated {table_name} foreign key")
            except Exception:
                print(f"⚠️ Could not update {table_name} foreign key")
    
    # Update alembic version
    op.execute("UPDATE alembic_version SET version_num = '20260319_000007'")
    print("✅ Updated alembic version")


def downgrade() -> None:
    # Complex downgrade - would require careful data migration
    pass
