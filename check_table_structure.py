"""Check and fix the cv_analyses table structure"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
db_url = os.getenv("DATABASE_URL", "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require")

print("=" * 80)
print("CHECKING CV_ANALYSES TABLE STRUCTURE")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get actual column details
    print("\n1. Getting detailed column information...")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'cv_analyses' 
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    
    print("   Current cv_analyses columns:")
    for col in columns:
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
        print(f"     - {col['column_name']}: {col['data_type']} {nullable}{default}")
    
    # Check for the specific columns our model expects
    print("\n2. Checking required columns...")
    required_columns = ['id', 'record_id', 'job_description', 'status', 'result', 'overall_score', 'component_scores', 'warnings', 'created_at', 'updated_at']
    
    for col in required_columns:
        exists = any(c['column_name'] == col for c in columns)
        status = "✅" if exists else "❌"
        print(f"   {status} {col}")
    
    # Check if there are any issues with the table
    print("\n3. Testing a simple insert...")
    try:
        cursor.execute("""
            INSERT INTO cv_analyses (id, record_id, job_description, status)
            VALUES (gen_random_uuid(), gen_random_uuid(), 'test', 'test')
        """)
        conn.rollback()  # Rollback the test insert
        print("   ✅ Insert test passed")
    except Exception as e:
        print(f"   ❌ Insert test failed: {e}")
        conn.rollback()
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("CHECK COMPLETE")
print("=" * 80)
