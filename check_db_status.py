import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection from .env
db_url = 'postgresql://recruitment_deploy_user:tHkpCaJ8nxQpN1tCItF7BEXNvzLrkgiQ@dpg-d62tb67pm1nc738h8jv0-a.oregon-postgres.render.com/recruitment_deploy?sslmode=require'

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check alembic version
    try:
        cursor.execute("SELECT version_num FROM alembic_version")
        result = cursor.fetchone()
        if result:
            print(f"Current alembic version in DB: {result['version_num']}")
            
            # Check if this revision exists in our migrations
            import os
            migration_dir = "migrations/versions"
            if os.path.exists(migration_dir):
                migrations = []
                for file in os.listdir(migration_dir):
                    if file.endswith('.py') and not file.startswith('__'):
                        with open(os.path.join(migration_dir, file), 'r') as f:
                            content = f.read()
                            if 'revision = ' in content:
                                for line in content.split('\n'):
                                    if line.strip().startswith('revision = '):
                                        rev = line.split('=')[1].strip().strip('"\'')
                                        migrations.append((rev, file))
                
                print("\nAvailable migrations:")
                for rev, file in migrations:
                    print(f"  {rev} - {file}")
                
                # Check if current version exists
                current_rev = result['version_num']
                exists = any(rev == current_rev for rev, _ in migrations)
                print(f"\nCurrent revision exists locally: {exists}")
        else:
            print("No alembic version found in database")
    except Exception as e:
        print(f"Error checking alembic version: {e}")
    
    # Check tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print("\nTables in database:")
    for table in tables:
        if 'cv' in table['table_name'].lower() or 'resume' in table['table_name'].lower():
            print(f"  - {table['table_name']}")
    
    conn.close()
    
except Exception as e:
    print(f"Error connecting to database: {e}")
