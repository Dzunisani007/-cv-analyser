from __future__ import annotations

import base64
import hashlib
import hmac
import time

from app.config import settings


def _secret_bytes() -> bytes:
    secret = settings.signing_secret or settings.auth_secret or ""
    return secret.encode("utf-8")


def sign_storage_key(storage_key: str, ttl_seconds: int = 300) -> str:
    exp = int(time.time()) + int(ttl_seconds)
    msg = f"{storage_key}:{exp}".encode("utf-8")
    sig = hmac.new(_secret_bytes(), msg, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(msg + b"." + sig).decode("utf-8")


def verify_signed_token(token: str) -> str:
    raw = base64.urlsafe_b64decode(token.encode("utf-8"))
    msg, sig = raw.rsplit(b".", 1)
    expected = hmac.new(_secret_bytes(), msg, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError("invalid signature")

    storage_key_s, exp_s = msg.decode("utf-8").split(":", 1)
    if int(exp_s) < int(time.time()):
        raise ValueError("expired")

    return storage_key_s
