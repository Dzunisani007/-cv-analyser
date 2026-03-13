from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_shape():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    payload = resp.json()
    assert "db" in payload
    assert "storage" in payload
    assert "models" in payload
    assert isinstance(payload["db"].get("ok"), bool)
