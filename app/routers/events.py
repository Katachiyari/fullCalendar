from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=list[schemas.Event])
async def read_events(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    events = await crud.get_events(db, skip=skip, limit=limit)
    return events

@router.post("/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: schemas.EventCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_event(event, db)

@router.get("/{event_id}", response_model=schemas.Event)
async def read_event(event_id: str, db: AsyncSession = Depends(get_db)):
    return await crud.get_event(event_id, db)

@router.put("/{event_id}", response_model=schemas.Event)
async def update_event(event_id: str, event: schemas.EventUpdate, db: AsyncSession = Depends(get_db)):
    # Vérifier que l'event n'est pas passé avant de le modifier
    existing_event = await crud.get_event(event_id, db)
    
    # Parser la date de démarrage de l'event existant
    try:
        event_start_str = existing_event.start.replace('Z', '+00:00')
        event_start_dt = datetime.fromisoformat(event_start_str)
    except (ValueError, AttributeError):
        event_start_dt = None
    
    # Si la date de démarrage est passée, interdire la modification
    if event_start_dt and event_start_dt.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible de modifier un évènement passé"
        )
    
    return await crud.update_event(event_id, event, db)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str, db: AsyncSession = Depends(get_db)):
    # Vérifier que l'event n'est pas passé avant de le supprimer
    existing_event = await crud.get_event(event_id, db)
    
    try:
        event_start_str = existing_event.start.replace('Z', '+00:00')
        event_start_dt = datetime.fromisoformat(event_start_str)
    except (ValueError, AttributeError):
        event_start_dt = None
    
    if event_start_dt and event_start_dt.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible de supprimer un évènement passé"
        )
    
    await crud.delete_event(event_id, db)
    return None
