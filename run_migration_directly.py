"""Run migration directly to debug"""
import os
import sys

# Set the new database URL
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"

print("Running migration directly...")

try:
    from alembic.config import Config
    from alembic import command
    from sqlalchemy import text
    
    alembic_cfg = Config("alembic.ini")
    
    # Get current engine
    from app.db import get_engine
    engine = get_engine()
    
    with engine.connect() as conn:
        # Enable UUID extension
        print("Enabling UUID extension...")
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        
        # Create cv_records table
        print("Creating cv_records table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cv_records (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                cv_text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """))
        
        # Create cv_analyses table
        print("Creating cv_analyses table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cv_analyses (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                record_id UUID NOT NULL REFERENCES cv_records(id) ON DELETE CASCADE,
                job_description TEXT,
                result JSON,
                overall_score FLOAT,
                component_scores JSON,
                status TEXT NOT NULL DEFAULT 'pending',
                warnings JSON,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                started_at TIMESTAMP WITH TIME ZONE,
                finished_at TIMESTAMP WITH TIME ZONE
            )
        """))
        
        # Create cv_resume_skills table
        print("Creating cv_resume_skills table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cv_resume_skills (
                id SERIAL PRIMARY KEY,
                resume_id UUID NOT NULL REFERENCES cv_records(id) ON DELETE CASCADE,
                skill TEXT,
                canonical_skill TEXT,
                match_score FLOAT,
                evidence JSON
            )
        """))
        
        # Create cv_resume_scores table
        print("Creating cv_resume_scores table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cv_resume_scores (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                resume_id UUID NOT NULL REFERENCES cv_records(id) ON DELETE CASCADE,
                overall_score FLOAT,
                component_scores JSON,
                explanation JSON,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """))
        
        # Create cv_audit_logs table
        print("Creating cv_audit_logs table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cv_audit_logs (
                id BIGSERIAL PRIMARY KEY,
                entity_type TEXT,
                entity_id UUID,
                action TEXT NOT NULL,
                actor_id UUID,
                payload JSON,
                ts TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """))
        
        # Create cv_workflow_audit_logs table
        print("Creating cv_workflow_audit_logs table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cv_workflow_audit_logs (
                id BIGSERIAL PRIMARY KEY,
                analysis_id UUID NOT NULL REFERENCES cv_analyses(id) ON DELETE CASCADE,
                from_stage TEXT,
                to_stage TEXT,
                action TEXT NOT NULL,
                actor_id UUID,
                reason TEXT,
                risk_assessment JSON,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
        """))
        
        # Update alembic version
        print("Updating alembic version...")
        conn.execute(text("""
            INSERT INTO alembic_version (version_num) 
            VALUES ('20260321_init_analyser_clean') 
            ON CONFLICT (version_num) DO UPDATE SET version_num = EXCLUDED.version_num
        """))
        
        conn.commit()
    
    print("\n✅ All tables created successfully!")
    
    # Verify tables
    print("\nVerifying tables...")
    inspector = engine.connect().exec_driver_sql("SELECT tablename FROM pg_tables WHERE schemaname = 'public'").fetchall()
    print(f"Tables found: {[row[0] for row in inspector]}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
