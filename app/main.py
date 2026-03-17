from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_session_factory
from app.api.routes_admin import router as admin_router
from app.api.routes_analyses import router as analyses_router
from app.api.routes_files import router as files_router
from app.api.routes_health import router as health_router
from app.api.routes_metrics import router as metrics_router
from app.api.routes_upload import router as upload_router
from app.tasks.job_queue import start_workers, stop_workers

app = FastAPI(title="CV Analyser Service")

if settings.allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"] ,
        allow_headers=["*"],
    )

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(analyses_router)
app.include_router(admin_router)
app.include_router(files_router)

if settings.prometheus_enabled:
    app.include_router(metrics_router)


@app.on_event("startup")
def _startup() -> None:
    init_session_factory()
    # Optional auto-migration on start (useful for Render one-off)
    import os

    if os.getenv("RUN_MIGRATIONS_ON_START", "false").lower() == "true":
        try:
            from alembic.config import Config
            from alembic import command

            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
        except Exception as e:
            # Log but do not crash the service
            import logging

            logging.getLogger(__name__).warning(f"Auto-migration failed: {e}")

    start_workers(settings.worker_count)
    # Best-effort warmup; can be skipped in tests.
    if (os.getenv("SKIP_MODEL_LOAD", "false") or "false").lower() != "true":
        try:
            from app.services.embedding_matcher import load_embed
            from app.services.ner_and_canon import load_ner

            load_ner()
            load_embed()
        except Exception:
            pass


@app.post("/migrate")
def _run_migrations():
    """Temporary endpoint to run migrations - remove after use"""
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        return {"status": "success", "message": "Migrations completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.on_event("shutdown")
def _shutdown() -> None:
    stop_workers()
