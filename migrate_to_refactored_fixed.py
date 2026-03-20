"""Fixed migration script - handle missing resume_text"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Database connection
db_url = "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require"

print("=" * 80)
print("DATABASE MIGRATION - CV_REFACTOR (FIXED)")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Begin transaction
    conn.autocommit = False
    
    try:
        # 1. Clean up - drop cv_records if it exists from previous failed migration
        print("\n1. Cleaning up previous migration...")
        cursor.execute("DROP TABLE IF EXISTS cv_records")
        cursor.execute("ALTER TABLE cv_analyser.cv_analyses DROP COLUMN IF EXISTS record_id")
        print("   ✅ Cleaned up previous migration")
        
        # 2. Create cv_records table
        print("\n2. Creating cv_records table...")
        cursor.execute("""
            CREATE TABLE cv_records (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                cv_text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("   ✅ cv_records table created")
        
        # 3. Migrate data from cv_resumes to cv_records (including empty resume_text)
        print("\n3. Migrating all data from cv_resumes to cv_records...")
        cursor.execute("""
            INSERT INTO cv_records (id, cv_text, status, created_at, updated_at)
            SELECT id, 
                   COALESCE(resume_text, 'No resume text available'), 
                   status, 
                   created_at, 
                   updated_at
            FROM public.cv_resumes
            ON CONFLICT (id) DO NOTHING
        """)
        
        cursor.execute("SELECT COUNT(*) FROM cv_records")
        result = cursor.fetchone()
        migrated_count = result['count'] if isinstance(result, dict) else list(result.values())[0]
        print(f"   ✅ Migrated {migrated_count} records to cv_records")
        
        # 4. Add record_id column to cv_analyses
        print("\n4. Adding record_id column to cv_analyses...")
        cursor.execute("""
            ALTER TABLE cv_analyser.cv_analyses 
            ADD COLUMN record_id UUID
        """)
        print("   ✅ record_id column added")
        
        # 5. Copy resume_id to record_id
        print("\n5. Copying resume_id to record_id...")
        cursor.execute("""
            UPDATE cv_analyser.cv_analyses 
            SET record_id = resume_id 
            WHERE record_id IS NULL AND resume_id IS NOT NULL
        """)
        
        cursor.execute("""
            SELECT COUNT(*) FROM cv_analyser.cv_analyses 
            WHERE record_id IS NOT NULL
        """)
        result = cursor.fetchone()
        updated_count = result['count'] if isinstance(result, dict) else list(result.values())[0]
        print(f"   ✅ Updated {updated_count} records with record_id")
        
        # 6. Add job_description column if not exists
        print("\n6. Adding job_description column...")
        cursor.execute("""
            ALTER TABLE cv_analyser.cv_analyses 
            ADD COLUMN IF NOT EXISTS job_description TEXT
        """)
        print("   ✅ job_description column added")
        
        # 7. Create indexes for performance
        print("\n7. Creating indexes...")
        cursor.execute("""
            CREATE INDEX ix_cv_records_status 
            ON cv_records (status)
        """)
        cursor.execute("""
            CREATE INDEX ix_cv_analyses_record_id 
            ON cv_analyser.cv_analyses (record_id)
        """)
        print("   ✅ Indexes created")
        
        # 8. Add foreign key constraint
        print("\n8. Adding foreign key constraint...")
        cursor.execute("""
            ALTER TABLE cv_analyser.cv_analyses 
            ADD CONSTRAINT cv_analyses_record_id_fkey 
            FOREIGN KEY (record_id) REFERENCES cv_records(id) 
            ON DELETE CASCADE
        """)
        print("   ✅ Foreign key constraint added")
        
        # 9. Verify migration
        print("\n9. Verifying migration...")
        cursor.execute("SELECT COUNT(*) FROM cv_records")
        result = cursor.fetchone()
        cv_records_count = result['count'] if isinstance(result, dict) else list(result.values())[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM cv_analyser.cv_analyses 
            WHERE record_id IS NOT NULL
        """)
        result = cursor.fetchone()
        linked_count = result['count'] if isinstance(result, dict) else list(result.values())[0]
        
        print(f"   cv_records count: {cv_records_count}")
        print(f"   cv_analyses with record_id: {linked_count}")
        
        # Commit transaction
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("MIGRATION COMPLETE")
print("=" * 80)
