from __future__ import annotations

from fastapi import Header, HTTPException

from app.config import settings


def require_bearer_auth(authorization: str | None = Header(default=None)) -> None:
    """Bearer auth guard.

    Option B behavior:
    - If AUTH_SECRET is unset AND PUBLIC_UPLOADS=true, allow anonymous access.
    - Otherwise require Authorization: Bearer <AUTH_SECRET>.
    """

    secret = settings.auth_secret
    if not secret:
        if settings.public_uploads:
            return
        raise HTTPException(status_code=401, detail="AUTH_SECRET is not configured")

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if token != secret:
        raise HTTPException(status_code=403, detail="invalid token")


def require_bearer_auth_strict(authorization: str | None = Header(default=None)) -> None:
    """Strict bearer auth guard.

    Always requires Authorization: Bearer <AUTH_SECRET>.
    """

    secret = settings.auth_secret
    if not secret:
        raise HTTPException(status_code=401, detail="AUTH_SECRET is not configured")

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if token != secret:
        raise HTTPException(status_code=403, detail="invalid token")
