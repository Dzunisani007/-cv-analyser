"""Check current database state"""
import os

# Set the new database URL
os.environ["DATABASE_URL"] = "postgresql://recruiter:zhubXkTYjieGoYevXB7jtHj5EdhNYmV7@dpg-d6v72fchg0os73ddre00-a.oregon-postgres.render.com/analyser_w2n9?sslmode=require"

print("Checking current database state...")

try:
    from sqlalchemy import inspect
    from app.db import get_engine
    
    engine = get_engine()
    inspector = inspect(engine)
    
    print("\nTables in database:")
    tables = inspector.get_table_names()
    for table in sorted(tables):
        print(f"  - {table}")
    
    # Check if cv_analyses table exists and its columns
    if 'cv_analyses' in tables:
        print("\n\ncv_analyses columns:")
        columns = inspector.get_columns('cv_analyses')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        print("\n\ncv_analyses foreign keys:")
        fks = inspector.get_foreign_keys('cv_analyses')
        for fk in fks:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # Check cv_resume_scores table
    if 'cv_resume_scores' in tables:
        print("\n\ncv_resume_scores foreign keys:")
        fks = inspector.get_foreign_keys('cv_resume_scores')
        for fk in fks:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # Check alembic version
    print("\n\nAlembic version table:")
    if 'alembic_version' in tables:
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            for row in result:
                print(f"  Current version: {row[0]}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
