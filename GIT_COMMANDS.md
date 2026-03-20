# Git Commands for CV Analyser Refactoring

## Step 1: Add all core changes
```bash
# Core refactoring changes
git add alembic.ini
git add app/api/routes_admin.py
git add app/config.py
git add app/main.py
git add app/models.py
git add app/tasks/pipeline.py
git add render.yaml
git add requirements.runtime.txt

# New analyze API
git add app/api/routes_analyze.py

# Migration files
git add migrations/versions/20260319_000004_rename_resume_to_cv_record.py
git add migrations/versions/20260319_000005_refactored_init.py
git add migrations/versions/20260319_000006_sqlite_init.py
git add migrations/versions/20260319_000007_production.py
git add migrations/versions/20260319_000008_final_merge.py
git add migrations/versions/52f5afe21ced_merge_heads.py

# Deployment files
git add Procfile

# Stage deletions (removed files)
git add app/api/routes_files.py
git add app/api/routes_upload.py
git add app/services/parser.py
git add app/utils/storage.py
git add check_cloudinary.py
git add debug_secret.py
git add debug_upload.py
git add direct_test.py
git add test_cloudinary_detailed.py
git add test_cloudinary_sendgrid.py
git add test_correct_secret.py
git add test_cv_upload.py
git add test_local_storage.py
```

## Step 2: Commit the changes
```bash
git commit -m "refactor: convert CV analyser to pure text processing

- Remove file storage dependencies (Cloudinary, PDF parsing)
- Replace Resume model with CVRecord (stores only cv_text)
- Add new /api/v1/analyze endpoint for JSON-based CV analysis
- Update CVAnalysis to use record_id and add job_description field
- Remove all upload/download routes and file handling code
- Add database migrations for schema changes
- Update deployment configurations
- Clean up dependencies in requirements.runtime.txt

Breaking changes:
- POST /upload endpoint removed
- New POST /api/v1/analyze endpoint with JSON payload
- Database schema updated (cv_records table replaces cv_resumes)"
```

## Step 3: Optional - Add documentation (separate commit)
```bash
git add CODEBASE_REPORT.md
git add DEPLOYMENT.md
git add DEPLOYMENT_FINAL.md
git add FINAL_STATUS.md
git add MIGRATION_SUMMARY.md
git add PRODUCTION_SETUP.md

git commit -m "docs: add deployment and migration documentation"
```

## Step 4: Push to remote
```bash
git push origin main
```

## Untracked Files (Optional)
These files are untracked and can be added if needed:
- `migrate_to_refactored.py` and `migrate_to_refactored_fixed.py` - Migration scripts
- `check_db*.py` - Database check scripts
- `deployment_check.py` - Deployment verification script
- `cv_analyser_test.db` - Local test database

You can add them with:
```bash
git add migrate_to_refactored.py migrate_to_refactored_fixed.py
git add check_db.py check_db_direct.py check_db_status.py
git add deployment_check.py
git commit -m "feat: add database migration and check scripts"
```
