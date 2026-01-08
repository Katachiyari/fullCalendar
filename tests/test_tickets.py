import pytest
from httpx import AsyncClient


async def register_user(client: AsyncClient, email: str, password: str) -> None:
    r = await client.post(
        "/auth/register",
        json={
            "first_name": "U",
            "last_name": "Test",
            "email": email,
            "age": 30,
            "phone_number": "0600000000",
            "job_title": "Dev",
            "password": password,
        },
    )
    assert r.status_code == 201, r.text


async def login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.mark.anyio
async def test_ticket_update_writes_audit(client: AsyncClient):
    await register_user(client, "user@example.com", "UserPass@123")
    token = await login(client, "user@example.com", "UserPass@123")

    # Create a ticket
    create = await client.post(
        "/v2/tickets",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Disk low", "severity": "P1", "source": "MANUAL", "payload": {"path": "/data"}},
    )
    assert create.status_code == 201, create.text
    ticket_id = create.json()["id"]

    # Update ticket (assign + workflow)
    upd = await client.patch(
        f"/v2/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"workflow_status": "IN_PROGRESS", "assigned_to": "admin@devops.example.com", "note": "triage"},
    )
    assert upd.status_code == 200, upd.text

    # Verify audit log exists
    from sqlalchemy import select
    from app.models import AuditLog
    from app.database import SessionLocal

    async with SessionLocal() as db:
        res = await db.execute(
            select(AuditLog).where(AuditLog.entity_type == "ticket", AuditLog.entity_id == ticket_id).order_by(AuditLog.created_at.asc())
        )
        entries = list(res.scalars().all())

    actions = [e.action for e in entries]
    assert "ticket.create" in actions
    assert "ticket.update" in actions
