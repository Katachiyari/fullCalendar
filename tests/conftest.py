from __future__ import annotations

import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Ensure the repository root is importable so tests can do `import app...`
# even when pytest is run from a subdirectory (e.g. `frontend/`).
REPO_ROOT = Path(__file__).resolve().parents[1]
repo_root_str = str(REPO_ROOT)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)


@pytest.fixture
async def test_app(tmp_path, monkeypatch):
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

    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal)

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    # Create an admin for tests
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
                email_verified=True,
            )
            db.add(admin)
            await db.commit()

    yield main.app


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
