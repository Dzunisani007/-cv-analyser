#!/bin/bash
# Git commit strategy for CV Analyser refactoring

echo "=== CV Analyser - Git Commit Strategy ==="
echo ""

# 1. First, let's add all the essential changes
echo "1. Adding core refactoring changes..."
git add alembic.ini
git add app/api/routes_admin.py
git add app/config.py
git add app/main.py
git add app/models.py
git add app/tasks/pipeline.py
git add render.yaml
git add requirements.runtime.txt

# 2. Add the new analyze route
echo "2. Adding new analyze API..."
git add app/api/routes_analyze.py

# 3. Add migration files
echo "3. Adding migration files..."
git add migrations/versions/20260319_000004_rename_resume_to_cv_record.py
git add migrations/versions/20260319_000005_refactored_init.py
git add migrations/versions/20260319_000006_sqlite_init.py
git add migrations/versions/20260319_000007_production.py
git add migrations/versions/20260319_000008_final_merge.py
git add migrations/versions/52f5afe21ced_merge_heads.py

# 4. Add deployment files
echo "4. Adding deployment files..."
git add Procfile

# 5. Stage deletions
echo "5. Staging removed files..."
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

# 6. Create commit
echo "6. Creating commit..."
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

echo ""
echo "✅ Changes committed successfully!"
echo ""
echo "Note: The following files are untracked and can be added later if needed:"
echo "- Documentation files (DEPLOYMENT*.md, *.md)"
echo "- Database scripts (migrate_to_refactored*.py)"
echo "- Check scripts (check_db*.py, deployment_check.py)"
echo "- Test database (cv_analyser_test.db)"
