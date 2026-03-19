import os
from dotenv import load_dotenv

load_dotenv()


def _getenv(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return v


def _getbool(name: str, default: str = "false") -> bool:
    return (_getenv(name, default) or default).lower() in ("1", "true", "yes", "y")


def _getint(name: str, default: str) -> int:
    return int(_getenv(name, default) or default)


class Settings:
    def __init__(self) -> None:
        self.environment = _getenv("ENVIRONMENT", "development")
        self.database_url = _getenv("DATABASE_URL")
        self.service_host = _getenv("SERVICE_HOST", "0.0.0.0")
        self.service_port = _getint("SERVICE_PORT", "8000")
        self.storage_backend = _getenv("STORAGE_BACKEND", "local")
        self.local_storage_path = _getenv("LOCAL_STORAGE_PATH", "./.storage")
        self.max_upload_mb = _getint("MAX_UPLOAD_MB", "15")
        self.s3_bucket = _getenv("S3_BUCKET")
        self.s3_region = _getenv("S3_REGION")
        self.s3_access_key = _getenv("S3_ACCESS_KEY")
        self.s3_secret_key = _getenv("S3_SECRET_KEY")
        self.auth_secret = _getenv("AUTH_SECRET")
        self.public_uploads = _getbool("PUBLIC_UPLOADS", "false")
        self.signing_secret = _getenv("SIGNING_SECRET")
        self.allow_origins = [
            o.strip()
            for o in (_getenv("ALLOW_ORIGINS", "") or "").split(",")
            if o.strip()
        ]

        # Cloudinary
        self.cloudinary_cloud_name = _getenv("CLOUDINARY_CLOUD_NAME")
        self.cloudinary_api_key = _getenv("CLOUDINARY_API_KEY")
        self.cloudinary_api_secret = _getenv("CLOUDINARY_API_SECRET")

        self.embed_model: str = _getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.ner_model: str = _getenv("NER_MODEL", "dslim/bert-base-NER")
        self.ner_mode: str = _getenv("NER_MODE", "transformers")
        self.gliner_model: str = _getenv("GLINER_MODEL", "urchade/gliner_base-v2.1")
        self.structured_extraction_model: str = _getenv("STRUCTURED_EXTRACTION_MODEL", "microsoft/DialoGPT-medium")
        self.enable_structured_extraction: bool = _getbool("ENABLE_STRUCTURED_EXTRACTION", "true")
        self.generation_model: str | None = _getenv("GENERATION_MODEL")
        self.hf_api_token: str | None = _getenv("HF_API_TOKEN")

        self.llm_mode = (_getenv("LLM_MODE", "none") or "none").lower()
        self.llama_model_path = _getenv("LLAMA_MODEL_PATH")

        self.worker_count = _getint("WORKER_COUNT", "2")
        self.pgvector_enabled = _getbool("PGVECTOR_ENABLED", "false")

        self.inline_jobs = _getbool("INLINE_JOBS", "false")
        self.prometheus_enabled = _getbool("PROMETHEUS_ENABLED", "true")
        self.debug = _getbool("DEBUG", "false")
        self.sentry_dsn = _getenv("SENTRY_DSN")


settings = Settings()
