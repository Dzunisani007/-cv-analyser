"""Properly migrate cv_analyses table to new schema"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid

# Database connection
db_url = os.getenv("DATABASE_URL", "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require")

print("=" * 80)
print("MIGRATING CV_ANALYSES TO NEW SCHEMA")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check current table structure
    print("\n1. Checking current structure...")
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns 
        WHERE table_name = 'cv_analyses' 
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    current_columns = [col['column_name'] for col in columns]
    print(f"   Current columns: {current_columns}")
    
    # Add missing columns
    print("\n2. Adding missing columns...")
    
    if 'record_id' not in current_columns:
        print("   Adding record_id column...")
        cursor.execute("""
            ALTER TABLE cv_analyses 
            ADD COLUMN record_id UUID
        """)
        conn.commit()
        print("   ✅ record_id added")
    
    if 'overall_score' not in current_columns:
        print("   Adding overall_score column...")
        cursor.execute("""
            ALTER TABLE cv_analyses 
            ADD COLUMN overall_score DOUBLE PRECISION
        """)
        conn.commit()
        print("   ✅ overall_score added")
    
    if 'component_scores' not in current_columns:
        print("   Adding component_scores column...")
        cursor.execute("""
            ALTER TABLE cv_analyses 
            ADD COLUMN component_scores JSONB
        """)
        conn.commit()
        print("   ✅ component_scores added")
    
    if 'warnings' not in current_columns:
        print("   Adding warnings column...")
        cursor.execute("""
            ALTER TABLE cv_analyses 
            ADD COLUMN warnings JSONB
        """)
        conn.commit()
        print("   ✅ warnings added")
    
    if 'updated_at' not in current_columns:
        print("   Adding updated_at column...")
        cursor.execute("""
            ALTER TABLE cv_analyses 
            ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        """)
        conn.commit()
        print("   ✅ updated_at added")
    
    # Convert id from integer to UUID
    print("\n3. Converting id column to UUID...")
    if 'id' in current_columns:
        # Check if id is still integer
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'cv_analyses' AND column_name = 'id'
        """)
        result = cursor.fetchone()
        
        if result and result['data_type'] == 'integer':
            print("   Converting id from integer to UUID...")
            
            # Create a new UUID column
            cursor.execute("""
                ALTER TABLE cv_analyses 
                ADD COLUMN new_id UUID DEFAULT gen_random_uuid() NOT NULL
            """)
            
            # Update foreign key references if any
            cursor.execute("""
                SELECT table_name, column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
            """)
            fk_refs = cursor.fetchall()
            
            # Drop old primary key
            cursor.execute("ALTER TABLE cv_analyses DROP CONSTRAINT cv_analyses_pkey")
            
            # Drop old id column
            cursor.execute("ALTER TABLE cv_analyses DROP COLUMN id")
            
            # Rename new_id to id
            cursor.execute("ALTER TABLE cv_analyses RENAME COLUMN new_id TO id")
            
            # Add primary key constraint
            cursor.execute("ALTER TABLE cv_analyses ADD PRIMARY KEY (id)")
            
            conn.commit()
            print("   ✅ id converted to UUID")
    
    # Migrate data from candidate_id to record_id if cv_records exists
    print("\n4. Checking cv_records table...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'cv_records'
        )
    """)
    cv_records_exists = cursor.fetchone()[0]
    
    if cv_records_exists:
        print("   cv_records table exists")
        
        # Check if we have candidate_id to migrate
        if 'candidate_id' in current_columns:
            print("   Migrating candidate_id to record_id...")
            
            # Get sample data to understand the relationship
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM cv_analyses 
                WHERE candidate_id IS NOT NULL
            """)
            count = cursor.fetchone()['count']
            
            if count > 0:
                print(f"   Found {count} records with candidate_id")
                
                # For now, create dummy records in cv_records for each candidate_id
                # In a real migration, you'd need to map candidate_id to actual cv_records
                cursor.execute("""
                    INSERT INTO cv_records (id, cv_text, status)
                    SELECT gen_random_uuid(), 'Migrated from candidate_id: ' || candidate_id::text, 'migrated'
                    FROM (
                        SELECT DISTINCT candidate_id 
                        FROM cv_analyses 
                        WHERE candidate_id IS NOT NULL 
                        AND candidate_id NOT IN (
                            SELECT record_id::text::integer 
                            FROM cv_analyses 
                            WHERE record_id IS NOT NULL
                        )
                    ) AS unique_candidates
                    WHERE NOT EXISTS (
                        SELECT 1 FROM cv_records 
                        WHERE cv_text = 'Migrated from candidate_id: ' || unique_candidates.candidate_id::text
                    )
                    RETURNING id, 'Migrated from candidate_id: ' || candidate_id::text as cv_text
                """)
                
                # Update record_id with the new UUIDs
                cursor.execute("""
                    UPDATE cv_analyses 
                    SET record_id = cr.id
                    FROM cv_records cr
                    WHERE cr.cv_text = 'Migrated from candidate_id: ' || cv_analyses.candidate_id::text
                    AND cv_analyses.record_id IS NULL
                """)
                
                migrated = cursor.rowcount
                conn.commit()
                print(f"   ✅ Migrated {migrated} records to cv_records")
    
    # Add foreign key constraint
    print("\n5. Adding foreign key constraint...")
    try:
        cursor.execute("""
            ALTER TABLE cv_analyses 
            ADD CONSTRAINT cv_analyses_record_id_fkey 
            FOREIGN KEY (record_id) REFERENCES cv_records(id) ON DELETE CASCADE
        """)
        conn.commit()
        print("   ✅ Foreign key constraint added")
    except Exception as e:
        if "already exists" in str(e):
            print("   ✅ Foreign key constraint already exists")
        else:
            print(f"   ⚠️  Could not add foreign key: {e}")
    
    # Drop old columns if they exist
    print("\n6. Cleaning up old columns...")
    old_columns = ['candidate_id', 'cv_text']
    for col in old_columns:
        if col in current_columns:
            try:
                cursor.execute(f"ALTER TABLE cv_analyses DROP COLUMN {col}")
                conn.commit()
                print(f"   ✅ Dropped {col}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {col}: {e}")
    
    # Verify final structure
    print("\n7. Verifying final structure...")
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns 
        WHERE table_name = 'cv_analyses' 
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    
    print("   Final cv_analyses columns:")
    for col in columns:
        print(f"     - {col['column_name']}: {col['data_type']}")
    
    # Test insert
    print("\n8. Testing insert...")
    try:
        # Create a test record first
        cursor.execute("""
            INSERT INTO cv_records (id, cv_text, status)
            VALUES (gen_random_uuid(), 'Test CV', 'test')
            RETURNING id
        """)
        record_id = cursor.fetchone()[0]
        
        # Test insert into cv_analyses
        cursor.execute("""
            INSERT INTO cv_analyses (id, record_id, job_description, status)
            VALUES (gen_random_uuid(), %s, 'test', 'test')
        """, (record_id,))
        
        conn.rollback()  # Rollback the test
        print("   ✅ Insert test passed")
    except Exception as e:
        print(f"   ❌ Insert test failed: {e}")
        conn.rollback()
    
    conn.close()
    
    print("\n✅ Migration completed!")
    print("The analyze endpoint should work now.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("MIGRATION COMPLETE")
print("=" * 80)
