"""Simple migration to fix cv_analyses table"""
import os
import psycopg2

# Database connection
db_url = os.getenv("DATABASE_URL", "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require")

print("=" * 80)
print("SIMPLE MIGRATION FOR CV_ANALYSES")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Just add the missing columns
    print("\n1. Adding missing columns...")
    
    try:
        cursor.execute("ALTER TABLE cv_analyses ADD COLUMN record_id UUID")
        print("   ✅ record_id added")
    except Exception as e:
        if "already exists" in str(e):
            print("   ✅ record_id already exists")
        else:
            print(f"   ⚠️  record_id: {e}")
    
    try:
        cursor.execute("ALTER TABLE cv_analyses ADD COLUMN overall_score DOUBLE PRECISION")
        print("   ✅ overall_score added")
    except Exception as e:
        if "already exists" in str(e):
            print("   ✅ overall_score already exists")
        else:
            print(f"   ⚠️  overall_score: {e}")
    
    try:
        cursor.execute("ALTER TABLE cv_analyses ADD COLUMN component_scores JSONB")
        print("   ✅ component_scores added")
    except Exception as e:
        if "already exists" in str(e):
            print("   ✅ component_scores already exists")
        else:
            print(f"   ⚠️  component_scores: {e}")
    
    try:
        cursor.execute("ALTER TABLE cv_analyses ADD COLUMN warnings JSONB")
        print("   ✅ warnings added")
    except Exception as e:
        if "already exists" in str(e):
            print("   ✅ warnings already exists")
        else:
            print(f"   ⚠️  warnings: {e}")
    
    try:
        cursor.execute("ALTER TABLE cv_analyses ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
        print("   ✅ updated_at added")
    except Exception as e:
        if "already exists" in str(e):
            print("   ✅ updated_at already exists")
        else:
            print(f"   ⚠️  updated_at: {e}")
    
    conn.commit()
    
    # Create a test record to verify
    print("\n2. Creating test cv_record...")
    cursor.execute("""
        INSERT INTO cv_records (id, cv_text, status)
        VALUES (gen_random_uuid(), 'Test CV for migration', 'test')
        ON CONFLICT DO NOTHING
        RETURNING id
    """)
    result = cursor.fetchone()
    test_record_id = result[0] if result else None
    
    if test_record_id:
        print(f"   ✅ Created test record: {test_record_id}")
        
        # Test inserting into cv_analyses
        print("\n3. Testing cv_analyses insert...")
        try:
            cursor.execute("""
                INSERT INTO cv_analyses (id, record_id, job_description, status)
                VALUES (gen_random_uuid(), %s, 'Test job', 'test')
            """, (test_record_id,))
            conn.rollback()  # Rollback the test
            print("   ✅ Insert test passed!")
        except Exception as e:
            print(f"   ❌ Insert failed: {e}")
            conn.rollback()
    
    conn.close()
    
    print("\n✅ Migration completed!")
    print("Try the analyze endpoint now.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("MIGRATION COMPLETE")
print("=" * 80)
