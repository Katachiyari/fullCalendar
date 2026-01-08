import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# DATABASE_URL - PostgreSQL (production)
# DATABASE_URL = "postgresql+asyncpg://devops:devops123@postgres:5432/calendar"

DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./calendar.db"

# DATABASE_URL - configurable via env (utile pour tests)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase): pass

async def get_db():
    async with SessionLocal() as session:
        yield session
