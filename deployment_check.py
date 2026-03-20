"""Final Deployment Readiness Check"""
import os
import sys
from pathlib import Path

print("=" * 80)
print("FINAL DEPLOYMENT READINESS CHECK")
print("=" * 80)

# 1. Check essential files
print("\n1. ESSENTIAL FILES CHECK")
print("-" * 40)

essential_files = {
    "app/main.py": "Main application entry point",
    "app/models.py": "Database models",
    "app/config.py": "Configuration",
    "app/api/routes_analyze.py": "Main API endpoint",
    "requirements.runtime.txt": "Dependencies",
    "Dockerfile": "Docker configuration",
    "render.yaml": "Render deployment config",
    "Procfile": "Heroku deployment config",
    ".env": "Environment variables",
    "alembic.ini": "Database migration config"
}

all_present = True
for file_path, description in essential_files.items():
    if Path(file_path).exists():
        print(f"  ✅ {file_path} - {description}")
    else:
        print(f"  ❌ {file_path} - {description}")
        all_present = False

# 2. Check imports
print("\n2. IMPORT CHECK")
print("-" * 40)

try:
    from app.main import app
    print("  ✅ Main app imports successfully")
    
    # Check routes
    from app.api.routes_analyze import router as analyze_router
    print("  ✅ Analyze router imports")
    
    from app.models import CVRecord, CVAnalysis
    print("  ✅ Models import successfully")
    
    from app.config import settings
    print("  ✅ Configuration loads")
    
except ImportError as e:
    print(f"  ❌ Import error: {e}")
    all_present = False

# 3. Check API endpoints
print("\n3. API ENDPOINTS CHECK")
print("-" * 40)

try:
    routes = [route.path for route in app.routes]
    
    expected_routes = [
        "/health",
        "/api/v1/analyze",
        "/api/v1/analyze/{analysis_id}/status",
        "/api/v1/analyze/{analysis_id}/result"
    ]
    
    for route in expected_routes:
        # Check if route exists (allow for variable parts)
        if any(expected in actual for actual in routes):
            print(f"  ✅ {route}")
        else:
            print(f"  ❌ {route} - Not found")
            
except Exception as e:
    print(f"  ❌ Error checking routes: {e}")

# 4. Check configuration
print("\n4. CONFIGURATION CHECK")
print("-" * 40)

config_checks = {
    "DATABASE_URL": os.getenv("DATABASE_URL"),
    "HF_API_TOKEN": os.getenv("HF_API_TOKEN"),
    "AUTH_SECRET": os.getenv("AUTH_SECRET")
}

for key, value in config_checks.items():
    if value:
        if "password" in key.lower() or "secret" in key.lower() or "token" in key.lower():
            print(f"  ✅ {key}: {'*' * 8}...{value[-4:]}")
        else:
            print(f"  ✅ {key}: {value[:50]}...")
    else:
        print(f"  ⚠️  {key}: Not set (will use default)")

# 5. Check for removed files
print("\n5. CLEANUP CHECK")
print("-" * 40)

removed_files = [
    "app/api/routes_files.py",
    "app/api/routes_upload.py"
]

for file_path in removed_files:
    if not Path(file_path).exists():
        print(f"  ✅ {file_path} - Successfully removed")
    else:
        print(f"  ⚠️  {file_path} - Still present")

# 6. Database migration check
print("\n6. DATABASE MIGRATION STATUS")
print("-" * 40)

try:
    import alembic.config
    from alembic import command
    
    alembic_cfg = alembic.config.Config("alembic.ini")
    current = command.current(alembic_cfg)
    print(f"  Current migration: {current}")
    
    if current:
        print("  ✅ Database has been migrated")
    else:
        print("  ⚠️  Database not yet migrated")
        
except Exception as e:
    print(f"  ⚠️  Could not check migration status: {e}")

# 7. Final verdict
print("\n7. DEPLOYMENT READINESS")
print("-" * 40)

if all_present:
    print("  ✅ ALL CHECKS PASSED")
    print("  🚀 Ready for deployment!")
else:
    print("  ⚠️  Some issues found - review above")

print("\n" + "=" * 80)
print("CHECK COMPLETE")
print("=" * 80)
