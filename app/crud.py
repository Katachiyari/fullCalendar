from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.models import Event, User, UserRole
from app.schemas import EventCreate, EventUpdate

async def get_events(db: AsyncSession, current_user: User, skip: int = 0, limit: int = 100):
    """
    Récupérer les événements en fonction du rôle de l'utilisateur:
    - ADMIN: tous les événements
    - MODERATOR: tous sauf ceux des ADMINs
    - USER: seulement ses propres événements
    """
    stmt = select(Event).where(Event.deleted_at.is_(None))
    
    if current_user.role == UserRole.USER:
        # USER ne voit que ses propres événements
        stmt = stmt.where(Event.owner_id == current_user.id)
    elif current_user.role == UserRole.MODERATOR:
        # MODERATOR voit tout sauf les événements des ADMINs
        # Joindre avec User pour filtrer par rôle du propriétaire
        stmt = stmt.join(User, Event.owner_id == User.id).where(User.role != UserRole.ADMIN)
    
    # ADMIN voit tout (pas de filtre supplémentaire)
    
    stmt = stmt.order_by(Event.start).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_event(event_in: EventCreate, owner_id: str, db: AsyncSession):
    """Créer un événement avec l'owner_id de l'utilisateur courant"""
    event_data = event_in.dict()
    event_data['owner_id'] = owner_id
    event = Event(**event_data)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

async def get_event(event_id: str, db: AsyncSession):
    result = await db.execute(select(Event).where(Event.id == event_id, Event.deleted_at.is_(None)))
    event = result.scalar_one_or_none()
    if event is None: raise ValueError("Event not found")
    return event

async def get_event_owner(event: Event, db: AsyncSession) -> User:
    """Récupérer le propriétaire d'un événement"""
    result = await db.execute(select(User).where(User.id == event.owner_id))
    owner = result.scalar_one_or_none()
    if owner is None:
        raise ValueError("Event owner not found")
    return owner

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
