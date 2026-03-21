"""Model caching utilities for HF Spaces."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Cache directory for models
MODEL_CACHE_DIR = Path("/app/models")
CACHE_INFO_FILE = MODEL_CACHE_DIR / "cache_info.json"

logger = logging.getLogger(__name__)


def ensure_cache_dir():
    """Ensure model cache directory exists."""
    MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_CACHE_DIR


def get_cache_info() -> Dict[str, Any]:
    """Get cached model information."""
    if CACHE_INFO_FILE.exists():
        import json
        try:
            with open(CACHE_INFO_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read cache info: {e}")
    return {}


def save_cache_info(info: Dict[str, Any]):
    """Save model cache information."""
    import json
    try:
        with open(CACHE_INFO_FILE, 'w') as f:
            json.dump(info, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save cache info: {e}")


def is_model_cached(model_name: str) -> bool:
    """Check if model is cached."""
    cache_info = get_cache_info()
    return model_name in cache_info.get("cached_models", [])


def mark_model_cached(model_name: str, model_path: str):
    """Mark a model as cached."""
    cache_info = get_cache_info()
    if "cached_models" not in cache_info:
        cache_info["cached_models"] = []
    
    if model_name not in cache_info["cached_models"]:
        cache_info["cached_models"].append(model_name)
        cache_info[f"{model_name}_path"] = model_path
        cache_info[f"{model_name}_cached_at"] = str(Path().cwd())
        save_cache_info(cache_info)
        logger.info(f"Model {model_name} marked as cached")
