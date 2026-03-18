from __future__ import annotations

import io
import os
import uuid
from pathlib import Path

import requests

from app.config import settings


# Lazy Cloudinary import
_cloudinary = None


def _get_cloudinary():
    global _cloudinary
    if _cloudinary is None:
        import cloudinary
        import cloudinary.api
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
        )
        _cloudinary = cloudinary
    return _cloudinary


def _safe_ext(filename: str | None) -> str:
    if not filename:
        return ""
    _, ext = os.path.splitext(filename)
    ext = (ext or "").lower()
    if len(ext) > 10:
        return ""
    return ext


def _folder_for_entity(entity_type: str = "resumes") -> str:
    return f"cv_analyser/{entity_type}"


def save_file(file_bytes: bytes, filename: str | None, content_type: str | None) -> dict:
    backend = (settings.storage_backend or "local").lower()

    if backend == "cloudinary":
        return _save_to_cloudinary(file_bytes, filename, content_type)

    if backend == "local":
        base = Path(settings.local_storage_path or "./.storage")
        base.mkdir(parents=True, exist_ok=True)
        key = f"{uuid.uuid4()}{_safe_ext(filename)}"
        path = base / key
        path.write_bytes(file_bytes)
        return {
            "storage_key": key,
            "size_bytes": len(file_bytes),
            "content_type": content_type,
        }

    if backend == "s3":
        raise RuntimeError("S3 storage backend is not implemented in PR3")

    raise RuntimeError(f"Unknown STORAGE_BACKEND: {backend}")


def _save_to_cloudinary(file_bytes: bytes, filename: str | None, content_type: str | None) -> dict:
    """Upload file to Cloudinary and return the public_id as storage_key."""
    cld = _get_cloudinary()

    # Determine resource type based on content_type
    resource_type = "raw"
    if content_type:
        if content_type.startswith("image/"):
            resource_type = "image"
        elif content_type == "application/pdf":
            resource_type = "raw"

    # Upload to Cloudinary
    folder = _folder_for_entity("resumes")
    file_ext = _safe_ext(filename)
    public_id = f"{str(uuid.uuid4())}{file_ext}"

    try:
        result = cld.uploader.upload(
            io.BytesIO(file_bytes),
            public_id=public_id,
            folder=folder,
            resource_type=resource_type,
            filename=filename or "file",
        )
        return {
            "storage_key": result["public_id"],  # Store Cloudinary public_id
            "cloudinary_url": result["secure_url"],  # Also store the URL for convenience
            "size_bytes": len(file_bytes),
            "content_type": content_type,
        }
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}")


def load_file_bytes(storage_key: str | None) -> bytes:
    if not storage_key:
        raise RuntimeError("resume storage_key is missing")

    backend = (settings.storage_backend or "local").lower()

    if backend == "cloudinary":
        return _load_from_cloudinary(storage_key)

    if backend == "local":
        base = Path(settings.local_storage_path or "./.storage")
        path = base / storage_key
        if not path.exists():
            raise FileNotFoundError(str(path))
        return path.read_bytes()

    if backend == "s3":
        raise RuntimeError("S3 storage backend is not implemented")

    raise RuntimeError(f"Unknown STORAGE_BACKEND: {backend}")


def _load_from_cloudinary(public_id: str) -> bytes:
    """Download file from Cloudinary using the public_id."""
    # Generate a download URL
    cld = _get_cloudinary()

    try:
        # Get the resource info to find the URL
        resource = cld.api.resource(public_id, resource_type="raw")
        url = resource.get("secure_url")
        if not url:
            raise FileNotFoundError(f"Cloudinary resource not found: {public_id}")

        # Download the file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise FileNotFoundError(f"Failed to download from Cloudinary: {e}")


def delete_file(storage_key: str | None) -> None:
    if not storage_key:
        return

    backend = (settings.storage_backend or "local").lower()

    if backend == "cloudinary":
        _delete_from_cloudinary(storage_key)
        return

    if backend == "local":
        base = Path(settings.local_storage_path or "./.storage")
        path = base / storage_key
        try:
            if path.exists():
                path.unlink()
        except Exception:
            return
        return

    if backend == "s3":
        raise RuntimeError("S3 storage backend is not implemented")

    raise RuntimeError(f"Unknown STORAGE_BACKEND: {backend}")


def _delete_from_cloudinary(public_id: str) -> None:
    """Delete file from Cloudinary using the public_id."""
    cld = _get_cloudinary()

    try:
        cld.uploader.destroy(public_id)
    except Exception:
        # Ignore deletion errors (file may not exist)
        pass


def get_file_url(storage_key: str | None, download: bool = False) -> str | None:
    """Get a URL for the file (Cloudinary direct URL or None for local)."""
    if not storage_key:
        return None

    backend = (settings.storage_backend or "local").lower()

    if backend == "cloudinary":
        # Return Cloudinary URL directly
        cld = _get_cloudinary()
        try:
            resource = cld.api.resource(storage_key)
            return resource.get("secure_url")
        except Exception:
            return None

    if backend == "local":
        # Local files need to be served via /files/download endpoint
        return None

    return None
