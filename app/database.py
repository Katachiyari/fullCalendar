import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
DATABASE_URL = "postgresql+asyncpg://devops:devops123@postgres:5432/calendar"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
class Base(DeclarativeBase): pass
async def get_db():
    async with SessionLocal() as session:
        yield session
