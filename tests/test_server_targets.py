import pytest
from httpx import AsyncClient


async def login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.mark.anyio
async def test_admin_can_add_server_target_and_get_metrics(client: AsyncClient, monkeypatch):
    # Login as default admin created in tests/conftest.py
    token = await login(client, "admin@devops.example.com", "Admin@123456")

    # Monkeypatch collector to avoid network/ssh in tests
    import app.routers.server as server_router

    async def fake_collect(*args, **kwargs):
        return {
            "target": {"host": "10.0.0.10", "ssh_port": 22, "disk_path": "/"},
            "reachable": True,
            "collected_at": "2026-01-08T00:00:00",
            "method": "mock",
            "error": None,
            "cpu": {"cores": 4, "load": {"avg_1": 0.1, "avg_5": 0.2, "avg_15": 0.3}},
            "memory": {"total_bytes": 1, "used_bytes": 1, "available_bytes": 1},
            "storage": {"path": "/", "total_bytes": 1, "used_bytes": 1, "free_bytes": 1},
        }

    monkeypatch.setattr(server_router, "collect_remote_metrics", fake_collect)

    create = await client.post(
        "/admin/servers",
        headers={"Authorization": f"Bearer {token}"},
        json={"host": "10.0.0.10", "name": "srv-ops-01"},
    )
    assert create.status_code == 201, create.text
    server_id = create.json()["id"]

    lst = await client.get("/admin/servers", headers={"Authorization": f"Bearer {token}"})
    assert lst.status_code == 200
    assert any(r["id"] == server_id for r in lst.json())

    metrics = await client.get(f"/admin/servers/{server_id}/metrics", headers={"Authorization": f"Bearer {token}"})
    assert metrics.status_code == 200, metrics.text
    assert metrics.json()["method"] == "mock"
