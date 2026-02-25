import os

os.environ["USE_MOCK_DATA"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test-kubeaico.db"
os.environ["DEFAULT_ADMIN_USERNAME"] = "admin"
os.environ["DEFAULT_ADMIN_PASSWORD"] = "admin123"

from fastapi.testclient import TestClient

from app.main import app


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_resource_detail_and_audit_logs_flow() -> None:
    with TestClient(app) as client:
        token = _login(client)
        headers = {"Authorization": f"Bearer {token}"}

        detail_resp = client.get(
            "/api/v1/resources/deployment/web/detail",
            params={"namespace": "default", "log_lines": 100},
            headers=headers,
        )
        assert detail_resp.status_code == 200
        detail_payload = detail_resp.json()
        assert detail_payload["item"]["name"] == "web"
        assert isinstance(detail_payload["manifest"], dict)
        assert detail_payload["manifest"]["metadata"]["name"] == "web"
        assert isinstance(detail_payload["events"], list)
        assert "metrics" in detail_payload
        assert detail_payload["metrics"]["range_minutes"] == 10
        assert len(detail_payload["metrics"]["series"]) >= 1

        logs_resp = client.get(
            "/api/v1/resources/deployment/web/logs",
            params={"namespace": "default", "log_lines": 100},
            headers=headers,
        )
        assert logs_resp.status_code == 200
        logs_payload = logs_resp.json()
        assert logs_payload["kind"] == "deployment"
        assert logs_payload["name"] == "web"
        assert isinstance(logs_payload["logs"], list)

        scale_resp = client.post(
            "/api/v1/resources/deployment/web/scale",
            json={"namespace": "default", "replicas": 3},
            headers=headers,
        )
        assert scale_resp.status_code == 200

        audit_resp = client.get(
            "/api/v1/audit/logs",
            params={"limit": 20},
            headers=headers,
        )
        assert audit_resp.status_code == 200
        audit_payload = audit_resp.json()
        assert audit_payload["total"] >= 1
        assert any(item["action"] == "scale" for item in audit_payload["items"])
