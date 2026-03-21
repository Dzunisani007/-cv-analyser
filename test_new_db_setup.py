"""Test new database setup and migration"""
import os
import sys

# Set the new database URL
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"

print("Testing new analyser database setup...")

try:
    # Test database connection
    from app.db import check_db
    db_status = check_db()
    print(f"Database connection: {db_status}")
    
    if not db_status.get("ok"):
        print("❌ Database connection failed")
        sys.exit(1)
    
    # Run migration
    print("\nRunning migration...")
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("✅ Migration completed")
    
    # Test creating a CV record
    print("\nTesting CV record creation...")
    from app.db import session_scope
    from app.models import CVRecord, CVAnalysis
    import uuid
    
    with session_scope() as db:
        record = CVRecord(cv_text="Test CV text for database setup", status="pending")
        db.add(record)
        db.flush()
        
        analysis = CVAnalysis(
            record_id=record.id,
            job_description="Test job description",
            status="pending"
        )
        db.add(analysis)
        db.flush()
        
        print(f"✅ Created CV record: {record.id}")
        print(f"✅ Created analysis: {analysis.id}")
    
    print("\n✅ Database setup test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
