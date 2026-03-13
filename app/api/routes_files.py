from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.auth import require_bearer_auth
from app.utils.signing import verify_signed_token
from app.utils.storage import load_file_bytes

router = APIRouter()


@router.get("/files/download")
def download_file(
    token: str = Query(...),
    _auth: None = Depends(require_bearer_auth),
):
    try:
        storage_key = verify_signed_token(token)
    except Exception:
        raise HTTPException(status_code=403, detail="invalid token")

    data = load_file_bytes(storage_key)
    return Response(content=data, media_type="application/octet-stream")
