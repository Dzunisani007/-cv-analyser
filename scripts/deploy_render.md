# Deploy to Render (Docker)

## Create service
- Create a new **Web Service** on Render.
- Choose **Docker**.
- Root directory: `service/`.
- Exposed port: `8000`.
- Health check path: `/health`.

## Required environment variables
- `DATABASE_URL` (Render Postgres URL)
- `AUTH_SECRET` (bearer token for admin endpoints; recommended to use for uploads too)
- `ALLOW_ORIGINS` (comma-separated origins)

## Optional environment variables
- `STORAGE_BACKEND` (default `local`)
- `LOCAL_STORAGE_PATH` (default `./.storage`)
- `MAX_UPLOAD_MB` (default `15`)
- `WORKER_COUNT` (default `2`)
- `EMBED_MODEL` (default `sentence-transformers/all-MiniLM-L6-v2`)
- `NER_MODEL` (default `dslim/bert-base-NER`)
- `LLM_MODE` (`none` recommended on Render)
- `PGVECTOR_ENABLED` (`false` by default)

## Notes
- OCR requires system packages (`tesseract-ocr`, `poppler-utils`) which are installed in the Dockerfile.
- If you want faster deploys on free instances, you can set `SKIP_MODEL_LOAD=true` to avoid downloading HF models at startup.

## Smoke test
1. `curl https://<render-service-url>/health`
2. Upload:

```bash
curl -X POST "https://<render-service-url>/upload" \
  -F "file=@./resume.txt" \
  -F "job_description=python docker postgres" 
```

3. Poll:

```bash
curl "https://<render-service-url>/analyses/<analysis_id>/status"
```
