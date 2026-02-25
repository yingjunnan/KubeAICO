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


def test_cluster_crud_flow() -> None:
    with TestClient(app) as client:
        token = _login(client)
        headers = {"Authorization": f"Bearer {token}"}

        create_resp = client.post(
            "/api/v1/clusters",
            json={
                "name": "prod-cluster",
                "cluster_id": "cluster-prod",
                "k8s_api_url": "https://k8s.example.com:6443",
                "prometheus_url": "http://prometheus:9090",
                "k8s_bearer_token": "secret-token-value",
                "is_active": True,
                "description": "production cluster",
            },
            headers=headers,
        )
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["k8s_bearer_token_masked"] is not None
        cluster_pk = created["id"]

        duplicate_name_resp = client.post(
            "/api/v1/clusters",
            json={
                "name": "prod-cluster",
                "cluster_id": "cluster-dup-name",
                "k8s_api_url": "https://k8s2.example.com:6443",
                "is_active": True,
            },
            headers=headers,
        )
        assert duplicate_name_resp.status_code == 400

        duplicate_cluster_id_resp = client.post(
            "/api/v1/clusters",
            json={
                "name": "prod-cluster-2",
                "cluster_id": "cluster-prod",
                "k8s_api_url": "https://k8s3.example.com:6443",
                "is_active": True,
            },
            headers=headers,
        )
        assert duplicate_cluster_id_resp.status_code == 400

        list_resp = client.get("/api/v1/clusters", headers=headers)
        assert list_resp.status_code == 200
        assert list_resp.json()["total"] >= 1

        update_resp = client.put(
            f"/api/v1/clusters/{cluster_pk}",
            json={"is_active": False, "description": "disabled for maintenance"},
            headers=headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["is_active"] is False

        delete_resp = client.delete(f"/api/v1/clusters/{cluster_pk}", headers=headers)
        assert delete_resp.status_code == 204
