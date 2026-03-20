import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
db_url = 'postgresql://recruitment_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitment_deploy?sslmode=require'

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check alembic version
    cursor.execute("SELECT version_num FROM alembic_version")
    result = cursor.fetchone()
    print(f"Current alembic version in DB: {result['version_num'] if result else 'None'}")
    
    # Check tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%cv%' OR table_name LIKE '%resume%'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print("\nTables:")
    for table in tables:
        print(f"  - {table['table_name']}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
