from fastapi import APIRouter

from app.db import check_db
from app.config import settings
from app.services.embedding_matcher import _use_hf_api as embed_use_hf_api
from app.services.ner_and_canon import _use_hf_api as ner_use_hf_api

router = APIRouter()


@router.post("/warmup")
def warmup_models():
    """Pre-load models to avoid cold start on first request."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from app.services.embedding_matcher import load_embed
        from app.services.ner_and_canon import load_ner
        
        logger.info("Loading models for warmup...")
        
        # Load models
        ner_model = load_ner()
        embed_model = load_embed()
        
        # Check if models are loaded
        ner_loaded = ner_model is not None and ner_model != "__skipped__"
        embed_loaded = embed_model is not None and embed_model != "__skipped__"
        
        logger.info(f"Models loaded - NER: {ner_loaded}, Embeddings: {embed_loaded}")
        
        return {
            "status": "success",
            "models": {
                "ner": "loaded" if ner_loaded else "skipped",
                "embeddings": "loaded" if embed_loaded else "skipped"
            }
        }
    except Exception as e:
        logger.error(f"Model warmup failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/health")
def health():
    db = check_db()
    storage_ok = True
    storage_error = None
    storage_mode = settings.storage_backend or "local"

    try:
        if storage_mode.lower() == "local":
            import os
            os.makedirs(settings.local_storage_path or "./.storage", exist_ok=True)
            storage_ok = True
        elif storage_mode.lower() == "cloudinary":
            # Storage removed - not needed for refactored service
            storage_ok = False
            storage_error = "Storage module removed - not needed for refactored service"
        else:
            storage_ok = False
            storage_error = f"Unknown storage backend: {storage_mode}"
    except Exception as e:
        storage_ok = False
        storage_error = str(e)

    models_ok = True
    models_error = None
    models_mode = "unknown"

    try:
        # Determine mode without actually loading heavy models in API mode
        if settings.hf_api_token and (embed_use_hf_api() or ner_use_hf_api()):
            models_mode = "hf_api"
        else:
            # Attempt local load
            from app.services.embedding_matcher import load_embed
            from app.services.ner_and_canon import load_ner

            load_ner()
            load_embed()
            models_mode = "local"
    except Exception as e:
        models_ok = False
        models_error = str(e)
        models_mode = "error"

    return {
        "db": db,
        "storage": {"ok": storage_ok, "mode": storage_mode, **({"error": storage_error} if storage_error else {})},
        "models": {"ok": models_ok, "mode": models_mode, **({"error": models_error} if models_error else {})},
    }
