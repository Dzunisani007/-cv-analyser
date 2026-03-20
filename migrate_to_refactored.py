"""Migration script to transform database for refactored CV analyser"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Database connection
db_url = "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require"

print("=" * 80)
print("DATABASE MIGRATION - CV_REFACTOR")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Begin transaction
    conn.autocommit = False
    
    try:
        # 1. Create cv_records table
        print("\n1. Creating cv_records table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cv_records (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                cv_text TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        print("   ✅ cv_records table created")
        
        # 2. Migrate data from cv_resumes to cv_records
        print("\n2. Migrating data from cv_resumes to cv_records...")
        cursor.execute("""
            INSERT INTO cv_records (id, cv_text, status, created_at, updated_at)
            SELECT id, resume_text, status, created_at, updated_at
            FROM public.cv_resumes
            WHERE resume_text IS NOT NULL AND resume_text != ''
            ON CONFLICT (id) DO NOTHING
        """)
        
        cursor.execute("SELECT COUNT(*) FROM cv_records")
        result = cursor.fetchone()
        migrated_count = result['count'] if isinstance(result, dict) else list(result.values())[0]
        print(f"   ✅ Migrated {migrated_count} records to cv_records")
        
        # 3. Add record_id column to cv_analyses
        print("\n3. Adding record_id column to cv_analyses...")
        cursor.execute("""
            ALTER TABLE cv_analyser.cv_analyses 
            ADD COLUMN IF NOT EXISTS record_id UUID
        """)
        print("   ✅ record_id column added")
        
        # 4. Copy resume_id to record_id
        print("\n4. Copying resume_id to record_id...")
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
        
        # 5. Add job_description column if not exists
        print("\n5. Adding job_description column...")
        cursor.execute("""
            ALTER TABLE cv_analyser.cv_analyses 
            ADD COLUMN IF NOT EXISTS job_description TEXT
        """)
        print("   ✅ job_description column added")
        
        # 6. Create indexes for performance
        print("\n6. Creating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_cv_records_status 
            ON cv_records (status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_cv_analyses_record_id 
            ON cv_analyser.cv_analyses (record_id)
        """)
        print("   ✅ Indexes created")
        
        # 7. Update foreign key constraint
        print("\n7. Updating foreign key constraint...")
        try:
            cursor.execute("""
                ALTER TABLE cv_analyser.cv_analyses 
                DROP CONSTRAINT IF EXISTS cv_analyses_resume_id_fkey
            """)
            cursor.execute("""
                ALTER TABLE cv_analyser.cv_analyses 
                ADD CONSTRAINT cv_analyses_record_id_fkey 
                FOREIGN KEY (record_id) REFERENCES cv_records(id) 
                ON DELETE CASCADE
            """)
            print("   ✅ Foreign key constraint updated")
        except Exception as e:
            print(f"   ⚠️  Could not update foreign key: {e}")
        
        # 8. Verify migration
        print("\n8. Verifying migration...")
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
