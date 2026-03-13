from fastapi.testclient import TestClient

from app.main import app


def test_upload_returns_202_and_ids():
    client = TestClient(app)
    resp = client.post(
        "/upload",
        files={"file": ("resume.txt", b"Hello world\nPython\n", "text/plain")},
    )
    assert resp.status_code == 202
    payload = resp.json()
    assert payload["status"] == "pending"
    assert "analysis_id" in payload
    assert "resume_id" in payload

    status = client.get(f"/analyses/{payload['analysis_id']}/status")
    assert status.status_code == 200
