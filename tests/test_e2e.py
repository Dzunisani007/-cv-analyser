import time

from fastapi.testclient import TestClient

from app.main import app


def test_e2e_upload_to_completed_status_and_result():
    with TestClient(app) as client:
        resp = client.post(
            "/upload",
            files={
                "file": (
                    "resume.txt",
                    b"Email: a@b.com\nPython Docker\n2019-2021\n",
                    "text/plain",
                )
            },
            data={"job_description": "python docker aws"},
        )
        assert resp.status_code == 202
        analysis_id = resp.json()["analysis_id"]

        status = None
        last_warnings = None
        for _ in range(50):
            s = client.get(f"/analyses/{analysis_id}/status")
            assert s.status_code == 200
            body = s.json()
            status = body["status"]
            last_warnings = body.get("warnings")
            if status in ("completed", "failed"):
                break
            time.sleep(0.05)

        assert status == "completed", f"analysis status={status} warnings={last_warnings}"

        r = client.get(f"/analyses/{analysis_id}/result")
        assert r.status_code == 200, f"result status={r.status_code} body={r.text}"
        payload = r.json()
        assert "overall_score" in payload
        assert "component_scores" in payload
        assert "evidence" in payload
        assert "suggestions" in payload
        assert "raw_payload" in payload

        ev = payload["evidence"]
        assert "matched_skills" in ev
        assert "missing_skills" in ev
