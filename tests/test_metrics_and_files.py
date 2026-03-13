from __future__ import annotations

import os
import time

from fastapi.testclient import TestClient
import pytest


def test_metrics_endpoint_returns_200_and_prometheus_content():
    # Ensure the endpoint is enabled via env
    os.environ["PROMETHEUS_ENABLED"] = "true"
    os.environ["SKIP_MODEL_LOAD"] = "true"
    os.environ["INLINE_JOBS"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test_metrics.db"
    os.environ["STORAGE_BACKEND"] = "local"
    os.environ["LOCAL_STORAGE_PATH"] = "./.storage_test_metrics"

    from app.main import app

    with TestClient(app) as client:
        r = client.get("/metrics")
        assert r.status_code == 200
        # Basic sanity: prometheus client output is text/plain
        assert r.headers["content-type"].startswith("text/plain")


def test_sign_and_verify_token_roundtrip():
    os.environ["SIGNING_SECRET"] = "test-secret"
    from app.utils.signing import sign_storage_key, verify_signed_token
    key = "sample-resume-key-12345.pdf"
    token = sign_storage_key(key, ttl_seconds=2)
    assert token

    # Should verify immediately
    out = verify_signed_token(token)
    assert out == key

    # Expired token should raise
    time.sleep(3)
    with pytest.raises(ValueError, match="expired"):
        verify_signed_token(token)


def test_invalid_token_raises():
    os.environ["SIGNING_SECRET"] = "test-secret"
    from app.utils.signing import verify_signed_token
    with pytest.raises(ValueError, match="invalid signature"):
        verify_signed_token("not-a-base64-token")


def test_download_endpoint_requires_auth_and_token():
    os.environ["AUTH_SECRET"] = "secret123"
    os.environ["SKIP_MODEL_LOAD"] = "true"
    os.environ["INLINE_JOBS"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///./test_files.db"
    os.environ["STORAGE_BACKEND"] = "local"
    os.environ["LOCAL_STORAGE_PATH"] = "./.storage_test_files"

    from app.main import app

    with TestClient(app) as client:
        # No auth header
        r = client.get("/files/download?token=any")
        assert r.status_code == 403

        # Auth header but no token query param
        r = client.get("/files/download", headers={"Authorization": "Bearer secret123"})
        assert r.status_code == 422

        # Auth + invalid token
        r = client.get("/files/download?token=invalid", headers={"Authorization": "Bearer secret123"})
        assert r.status_code == 403
