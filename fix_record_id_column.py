"""Fix the missing record_id column in cv_analyses table"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
db_url = os.getenv("DATABASE_URL", "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require")

print("=" * 80)
print("FIXING MISSING record_id COLUMN")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if record_id column exists
    print("\n1. Checking if record_id column exists...")
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'cv_analyses' AND column_name = 'record_id'
    """)
    result = cursor.fetchone()
    
    if result:
        print("   record_id column already exists")
    else:
        print("   record_id column is missing - adding it...")
        
        # Add the record_id column
        cursor.execute("""
            ALTER TABLE cv_analyses 
            ADD COLUMN record_id UUID REFERENCES cv_records(id) ON DELETE CASCADE
        """)
        conn.commit()
        print("   record_id column added successfully")
        
        # Check if we need to migrate data from resume_id
        print("\n2. Checking for existing resume_id column...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'cv_analyses' AND column_name = 'resume_id'
        """)
        result = cursor.fetchone()
        
        if result:
            print("   Found resume_id column - migrating data...")
            # Migrate data from resume_id to record_id
            cursor.execute("""
                UPDATE cv_analyses 
                SET record_id = resume_id 
                WHERE resume_id IS NOT NULL AND record_id IS NULL
            """)
            migrated = cursor.rowcount
            conn.commit()
            print(f"   Migrated {migrated} records from resume_id to record_id")
            
            # Optionally drop the old column after successful migration
            print("\n3. Dropping old resume_id column...")
            cursor.execute("ALTER TABLE cv_analyses DROP COLUMN resume_id")
            conn.commit()
            print("   resume_id column dropped")
    
    # Verify the fix
    print("\n4. Verifying the fix...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'cv_analyses' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print("   cv_analyses columns:")
    for col in columns:
        print(f"     - {col['column_name']}: {col['data_type']}")
    
    conn.close()
    
    print("\n✅ Database schema fixed!")
    print("The analyze endpoint should work now.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIX COMPLETE")
print("=" * 80)
