import os


os.environ["AUTO_CREATE_SCHEMA"] = "true"
os.environ["JWT_SECRET"] = "test-secret-that-is-at-least-thirty-two-bytes"
os.environ["ADMIN_PASSWORD"] = "test-password"

from fastapi.testclient import TestClient

from app.main import app


def setup_function():
    from app.db import Base, engine
    Base.metadata.drop_all(engine)


def test_scan_returns_explainable_high_risk_result():
    with TestClient(app) as client:
        token = client.post("/auth/token?username=admin&password=test-password").json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/scans", headers=headers, json={"url": "https://sbi-secure-login.zip/verify", "enrichment": {"registration_age_days": 2, "visual_similarity": 0.90, "credential_form_detected": True, "external_form_action": True}})
        assert response.status_code == 201
        body = response.json()
        assert body["target_brand"]["name"] == "State Bank of India"
        assert body["risk_level"] in {"high", "critical"}
        assert body["explanation"]
        verdict = client.put(f"/scans/{body['id']}/verdict", headers=headers, json={"verdict": "phishing", "note": "Controlled test fixture"})
        assert verdict.status_code == 200
        assert verdict.json()["status"] == "phishing"


def test_ip_targets_are_rejected():
    with TestClient(app) as client:
        token = client.post("/auth/token?username=admin&password=test-password").json()["access_token"]
        response = client.post("/scans", headers={"Authorization": f"Bearer {token}"}, json={"url": "http://127.0.0.1/admin"})
        assert response.status_code == 422
