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


def test_overview_summary_endpoint() -> None:
    with TestClient(app) as client:
        token = _login(client)
        response = client.get(
            "/api/v1/overview/summary",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert "risk_score" in payload
    assert payload["nodes_total"] >= payload["nodes_ready"]


def test_resources_and_ai_flow() -> None:
    with TestClient(app) as client:
        token = _login(client)
        headers = {"Authorization": f"Bearer {token}"}

        resources_resp = client.get("/api/v1/resources/deployment", headers=headers)
        assert resources_resp.status_code == 200
        assert resources_resp.json()["total"] >= 1

        analyze_resp = client.post(
            "/api/v1/ai/analyze",
            headers=headers,
            json={
                "metrics": [
                    {"name": "cpu_utilization", "value": 85},
                    {"name": "memory_utilization", "value": 88},
                ],
                "events": [],
            },
        )
        assert analyze_resp.status_code == 202

        task_id = analyze_resp.json()["task_id"]

        task_resp = client.get(f"/api/v1/ai/tasks/{task_id}", headers=headers)
        assert task_resp.status_code == 200
        assert task_resp.json()["status"] in {"running", "completed", "pending"}
