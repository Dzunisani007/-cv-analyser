# CV Analyser Service (Backend)

## Environment variables

- **`ENVIRONMENT`**: `development|staging|production`.
- **`SERVICE_HOST`**: bind host (default `0.0.0.0`).
- **`SERVICE_PORT`**: bind port (default `8000`).
- **`ALLOW_ORIGINS`**: comma-separated CORS origins.

- **`AUTH_SECRET`**: bearer token secret.
- **`PUBLIC_UPLOADS`**: Option B toggle.
  - If `AUTH_SECRET` is unset and `PUBLIC_UPLOADS=true`, `/upload` is allowed without an `Authorization` header.
  - If `AUTH_SECRET` is set, `/upload` requires `Authorization: Bearer <AUTH_SECRET>`.
- **`SIGNING_SECRET`**: reserved for signed URLs (future).

- **`DATABASE_URL`**: Postgres connection string.
- **`PGVECTOR_ENABLED`**: `true|false` (optional).

- **`STORAGE_BACKEND`**: `local|s3`.
- **`LOCAL_STORAGE_PATH`**: local disk path when `STORAGE_BACKEND=local`.
- **`S3_BUCKET`, `S3_REGION`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`**: required when `STORAGE_BACKEND=s3`.

- **`EMBED_MODEL`**: sentence-transformers model id.
- **`NER_MODEL`**: Hugging Face NER model id.

- **`LLM_MODE`**: `none|local`.
- **`LLAMA_MODEL_PATH`**: required when `LLM_MODE=local`.

- **`WORKER_COUNT`**: background worker threads (default `2`).
- **`INLINE_JOBS`**: run jobs inline (useful in tests).
- **`MAX_UPLOAD_MB`**: upload size cap.
- **`PROMETHEUS_ENABLED`**: enable metrics endpoint (future).
- **`DEBUG`**: debug toggle.
- **`SENTRY_DSN`**: optional monitoring.
- **`RUN_MIGRATIONS_ON_START`**: set to `true` once to auto-run Alembic migrations on startup (use with care).

Copy `.env.example` to `.env` and adjust values.

## Run locally (dev)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run locally (Ubuntu WSL)

```bash
cd service
chmod +x scripts/*.sh

./scripts/setup_venv.sh
./scripts/test.sh
./scripts/run_local_wsl.sh
```

If you want Postgres locally, use Docker Compose:

```bash
cd service
cp .env.example .env
docker-compose up --build
```

### Run locally (PowerShell)

```powershell
Copy-Item .env.example .env
# edit .env

# Load .env into current session
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
  $name, $value = $_ -split '=', 2
  $env:$name = $value
}

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q

uvicorn app.main:app --reload --host $env:SERVICE_HOST --port $env:SERVICE_PORT
```

### Run locally (Docker Compose)

```bash
cp .env.example .env
docker-compose up --build
```

### Upload test

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "Authorization: Bearer <AUTH_SECRET>" \
  -F "file=@./samples/resume.txt" \
  -F "job_description=python docker aws"
```

If running with `PUBLIC_UPLOADS=true` and `AUTH_SECRET` unset, omit the `Authorization` header.

## Test

```bash
python -m pytest -q
```

## Health check

```bash
curl http://localhost:8000/health
```

Expected keys:

- `db.ok`
- `storage.ok`
- `models.ok`

## Metrics

If `PROMETHEUS_ENABLED=true`, the service exposes `GET /metrics` (Prometheus format).

## Signed resume download

1) Obtain a signed download token (admin-only):

```bash
curl -X POST "http://127.0.0.1:8000/admin/resumes/{resume_id}/download-token" \
  -H "Authorization: Bearer <AUTH_SECRET>"
```

Response:
```json
{
  "token": "eyJzdG9yYWdlX2tleSI6InNh...",
  "expires_in": 300
}
```

2) Download the file using the token (auth required):

```bash
curl -L "http://127.0.0.1:8000/files/download?token=<TOKEN>" \
  -H "Authorization: Bearer <AUTH_SECRET>" \
  -o resume.pdf
```

Tokens expire after 5 minutes by default. The signing secret is `SIGNING_SECRET` (or falls back to `AUTH_SECRET`).

## GDPR delete

```bash
curl -X DELETE "http://127.0.0.1:8000/admin/resumes/{resume_id}" \
  -H "Authorization: Bearer <AUTH_SECRET>"
```

Deletes the resume file from storage and removes the DB row (cascade deletes analyses).

## CV Analysis Result Schema (v1)

The API always returns a versioned JSON structure for `CVAnalysis.result` to avoid key collisions and separate extraction from match analysis.

### Top-level keys
- `schema_version`: "v1"
- `extraction_metadata`: {method, confidence, pages, has_scanned_content}
- `structured_data`: {personal_details, education_details, professional_details}
- `match_analysis`: {overall_score, component_scores, evidence, match_suggestions, interview_questions}
- `extraction_suggestions`: [] (e.g., “Add a LinkedIn URL”)
- `raw_payload`: {entities, skill_matches}

### Backward compatibility
If a stored result lacks `schema_version`, the API adapts it to v1 on read, so UI code always sees the same shape.

### Example snippet
```json
{
  "schema_version": "v1",
  "extraction_metadata": {"method": "pdfplumber", "pages": 2, "has_scanned_content": false},
  "structured_data": {
    "personal_details": {"full_name": "...", "email": "..."},
    "education_details": {"education": [], "certifications": [], "languages": []},
    "professional_details": {"skills": [...], "experience": "..."}
  },
  "match_analysis": {
    "overall_score": 78,
    "component_scores": {"skills": 0.8, "experience": 0.7, "education": 0.9, "format": 0.6},
    "evidence": {"matched_skills": [...], "missing_skills": [...], "timeline": [...]},
    "match_suggestions": ["Add more quantifiable achievements"],
    "interview_questions": []
  },
  "extraction_suggestions": ["Add a LinkedIn URL to your profile."],
  "raw_payload": {"entities": {...}, "skill_matches": [...]}
}
```

## Deploy to Render

### 1) Create a Web Service (Docker)
- Connect your GitHub repo.
- Set **Service Port**: `8000`.
- Choose **Docker** environment.

### 2) Environment Variables (Render)
Add the following in Render > Environment:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
AUTH_SECRET=your-production-secret
PUBLIC_UPLOADS=false
SIGNING_SECRET=optional-signing-secret
PROMETHEUS_ENABLED=true
WORKER_COUNT=2
INLINE_JOBS=false
MAX_UPLOAD_MB=15
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./.storage
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
NER_MODEL=dslim/bert-base-NER
# Optional: GENERATION_MODEL=mistralai/Mistral-7B-Instruct-v0.1
# Optional: HF_API_TOKEN=your_hf_token
# Optional: RUN_MIGRATIONS_ON_START=true (run once, then set back to false)
```

### 3) One-time database migration
After the first deploy, run migrations once:

**Option A (recommended): Render Shell**
- Open your service > Shell.
- Run: `alembic upgrade head`

**Option B: auto-migrate on start**
- Temporarily set `RUN_MIGRATIONS_ON_START=true` in Render Environment.
- Redeploy. After a successful start, set it back to `false`.

### 4) Verify
- Health: `https://your-app.onrender.com/health`
- Metrics (if enabled): `https://your-app.onrender.com/metrics`

### 5) Storage note
- The default `STORAGE_BACKEND=local` stores files in the container’s ephemeral disk. This is acceptable for demos but files are lost on restarts.
- For production, implement Cloudinary or S3 storage and set `STORAGE_BACKEND=cloudinary` (you’ll need to add a Cloudinary backend in `app/utils/storage.py`).

### 6) Optional Cloudinary integration
If you want durable file storage:
- Add `cloudinary` to requirements.txt.
- Implement a Cloudinary storage backend in `app/utils/storage.py`.
- Set `STORAGE_BACKEND=cloudinary` and use the Cloudinary env vars you already have (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`).

### 7) Hugging Face model options
- **Local models (default)**: Downloads sentence-transformers and NER models on startup. Larger image, slower cold starts.
- **HF Inference API**: Set `HF_API_TOKEN`. The service calls HF APIs instead of loading local models. Use `Dockerfile.hf-api` for a slim image.
- **Generation**: Set `GENERATION_MODEL` plus `HF_API_TOKEN` to enable AI-generated interview questions and suggestions.

Do not commit `.env` to git.
