import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


@pytest.fixture
async def test_app(tmp_path, monkeypatch):
    # Isoler la DB par test sans recharger les modules (évite les doublons SQLAlchemy)
    db_path = tmp_path / "test_calendar.db"
    test_url = f"sqlite+aiosqlite:///{db_path}"

    import app.database as database
    import app.models as models
    import app.main as main

    engine = create_async_engine(
        test_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Patch engine/session utilisés par get_db + CRUD
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal)

    # Créer les tables
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    # Créer un admin (équivalent seed) dans la DB de test
    from sqlalchemy import select
    from app.security import hash_password
    from app.models import User, UserRole

    async with SessionLocal() as db:
        res = await db.execute(select(User).where(User.role == UserRole.ADMIN))
        existing = res.scalar_one_or_none()
        if not existing:
            admin = User(
                first_name="Admin",
                last_name="System",
                email="admin@devops.example.com",
                phone_number="+33600000000",
                age=30,
                job_title="System Administrator",
                hashed_password=hash_password("Admin@123456"),
                is_active=True,
                role=UserRole.ADMIN,
            )
            db.add(admin)
            await db.commit()

    yield main.app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


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


@pytest.mark.anyio
async def test_admin_can_delete_past_event_only(client: AsyncClient):
    # Create normal user and a past event owned by that user
    user_email = "user@example.com"
    user_password = "UserPass@123"
    await register_user(client, user_email, user_password)
    user_token = await login(client, user_email, user_password)

    create = await client.post(
        "/events/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "title": "Past",
            "start": "2025-01-01T10:00:00",
            "end": "2025-01-01T11:00:00",
            "all_day": False,
        },
    )
    assert create.status_code == 201, create.text
    event_id = create.json()["id"]

    # USER cannot delete past event
    del_user = await client.delete(
        f"/events/{event_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert del_user.status_code == 403

    # ADMIN can delete past event
    admin_token = await login(client, "admin@devops.example.com", "Admin@123456")
    del_admin = await client.delete(
        f"/events/{event_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert del_admin.status_code == 204
