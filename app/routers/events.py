from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import app.crud as crud
import app.schemas as schemas
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user, check_permission
from app.models import UserRole

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=list[schemas.Event])
async def read_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lister les événements en fonction du rôle:
    - ADMIN: tous les événements
    - MODERATOR: tous sauf ceux des ADMINs
    - USER: seulement ses propres événements
    """
    events = await crud.get_events(db, current_user, skip=skip, limit=limit)
    return events

@router.post("/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: schemas.EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer un événement. L'owner_id sera l'utilisateur courant.
    Tous les rôles peuvent créer des événements.
    """
    return await crud.create_event(event, current_user.id, db)

@router.get("/{event_id}", response_model=schemas.Event)
async def read_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer un événement par son ID.
    Vérifie les permissions d'accès.
    """
    event = await crud.get_event(event_id, db)
    owner = await crud.get_event_owner(event, db)
    
    # Vérifier les permissions
    check_permission(current_user, owner)
    
    return event

@router.put("/{event_id}", response_model=schemas.Event)
async def update_event(
    event_id: str,
    event: schemas.EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mettre à jour un événement.
    Vérifie que l'utilisateur a la permission et que l'événement n'est pas passé.
    """
    # Vérifier que l'event n'est pas passé avant de le modifier
    existing_event = await crud.get_event(event_id, db)
    
    # Vérifier les permissions
    owner = await crud.get_event_owner(existing_event, db)
    check_permission(current_user, owner)
    
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
async def delete_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprimer un événement (soft delete).
    Vérifie que l'utilisateur a la permission et que l'événement n'est pas passé.
    """
    # Vérifier que l'event n'est pas passé avant de le supprimer
    existing_event = await crud.get_event(event_id, db)
    
    # Vérifier les permissions
    owner = await crud.get_event_owner(existing_event, db)
    check_permission(current_user, owner)
    
    try:
        event_start_str = existing_event.start.replace('Z', '+00:00')
        event_start_dt = datetime.fromisoformat(event_start_str)
    except (ValueError, AttributeError):
        event_start_dt = None
    
    # Seul l'ADMIN peut supprimer un événement passé
    if (
        event_start_dt
        and event_start_dt.replace(tzinfo=None) < datetime.utcnow()
        and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible de supprimer un évènement passé"
        )
    
    await crud.delete_event(event_id, db)
    return None
