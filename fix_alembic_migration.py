"""Fix Alembic migration issue for production"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
db_url = os.getenv("DATABASE_URL", "postgresql://recruitement_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitement_deploy?sslmode=require")

print("=" * 80)
print("FIXING ALEMBIC MIGRATION ISSUE")
print("=" * 80)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check current alembic version
    print("\n1. Checking current Alembic version...")
    cursor.execute("SELECT version_num FROM alembic_version")
    result = cursor.fetchone()
    current_version = result['version_num'] if isinstance(result, dict) else list(result.values())[0]
    print(f"   Current version: {current_version}")
    
    # Update to the correct version (latest migration)
    print("\n2. Updating Alembic version to latest...")
    latest_version = "20260319_000008"  # This is our final merge migration
    cursor.execute("UPDATE alembic_version SET version_num = %s", (latest_version,))
    conn.commit()
    print(f"   Updated to: {latest_version}")
    
    # Verify update
    print("\n3. Verifying update...")
    cursor.execute("SELECT version_num FROM alembic_version")
    result = cursor.fetchone()
    new_version = result['version_num'] if isinstance(result, dict) else list(result.values())[0]
    print(f"   New version: {new_version}")
    
    conn.close()
    
    print("\n✅ Migration issue fixed!")
    print("The service should now start without migration errors.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIX COMPLETE")
print("=" * 80)
