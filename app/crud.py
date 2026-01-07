from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from models import Event
from schemas import EventCreate, EventUpdate
async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Event).where(Event.deleted_at.is_(None)).order_by(Event.start)
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()
async def create_event(event_in: EventCreate, db: AsyncSession):
    event = Event(**event_in.dict())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
async def get_event(event_id: str, db: AsyncSession):
    result = await db.execute(select(Event).where(Event.id == event_id, Event.deleted_at.is_(None)))
    event = result.scalar_one_or_none()
    if event is None: raise ValueError("Event not found")
    return event
async def update_event(event_id: str, event_in: EventUpdate, db: AsyncSession):
    event = await get_event(event_id, db)
    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
async def delete_event(event_id: str, db: AsyncSession):
    event = await get_event(event_id, db)
    event.deleted_at = func.now()
    db.add(event)
    await db.commit()
    return event
