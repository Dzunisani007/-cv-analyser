# Deployment Checklist

## Prerequisites
- Python 3.12+ environment
- PostgreSQL database (or SQLite for development)
- (Optional) Hugging Face API token for cloud models
- (Optional) Cloudinary/S3 credentials for file storage

## Environment Variables
Copy `.env.example` to `.env` and configure:
- `DATABASE_URL`: PostgreSQL connection string (required)
- `AUTH_SECRET`: Bearer token for securing endpoints (production)
- `PUBLIC_UPLOADS`: Set to `false` in production
- `SIGNING_SECRET`: Secret for signed download tokens
- `STORAGE_BACKEND`: `local`, `cloudinary`, or `s3`
- If `cloudinary`: set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- If `s3`: set `S3_BUCKET`, `S3_REGION`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- `HF_API_TOKEN`: Optional, enables cloud-based models
- `PROMETHEUS_ENABLED`: Set to `true` to expose `/metrics`
- `INLINE_JOBS`: Set to `true` to skip background worker (single-process mode)

## Database Setup
1. Ensure PostgreSQL is running and accessible via `DATABASE_URL`
2. Run migrations:
   ```bash
   export DATABASE_URL=postgresql+psycopg2://user:pass@host/db
   alembic upgrade head
   ```
   Note: `alembic.ini` uses `%(DATABASE_URL)s` interpolation; the env.py overrides it at runtime, so the variable must be present in the environment.

## Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Service
- Development: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Production: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`
- Docker Compose: `docker-compose up -d` (starts PostgreSQL and the service)

## Health Checks
- `/health`: Checks DB, storage, and model availability
- `/metrics`: Prometheus metrics (if enabled)

## Security Notes
- Set `AUTH_SECRET` to a strong random string in production
- Disable `PUBLIC_UPLOADS` when using auth
- Ensure storage backend credentials are kept secret
- Use `https` in production

## Troubleshooting
- If Alembic fails with interpolation error, ensure `DATABASE_URL` is exported before running `alembic`.
- For model loading errors, set `SKIP_MODEL_LOAD=true` to defer loading to first request.
- Use `INLINE_JOBS=true` for single-process deployments (no external worker).
