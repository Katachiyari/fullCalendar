from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import app.crud as crud
import app.schemas as schemas
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
from app.models import UserRole
from app.permissions import can_assign_events_to_any_group, can_manage_all_events
from app.permissions import visible_group_slugs_for_user
from app.models import Group
from sqlalchemy import select

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
    """Créer un événement.

    Cahier des charges:
    - Tant que l'email n'est pas vérifié: pas de création de RDV (sauf ADMIN).
    - Par défaut, l'événement est assigné au groupe de l'utilisateur.
    - Chef de projet / ADMIN peuvent assigner à un autre groupe.
    """
    if current_user.role != UserRole.ADMIN and not getattr(current_user, "email_verified", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email non vérifié: création de rendez-vous interdite",
        )

    payload = event
    if not can_assign_events_to_any_group(current_user):
        # Forcer au groupe de l'utilisateur (ou None)
        payload = schemas.EventCreate(**{**event.model_dump(), "group_id": current_user.group_id})
    else:
        if event.group_id is None:
            payload = schemas.EventCreate(**{**event.model_dump(), "group_id": current_user.group_id})

        # Cahier des charges (et UX actuelle): un événement doit être rattaché à un groupe.
        # Si l'utilisateur n'a pas de groupe, l'admin doit l'assigner avant création.
        if payload.group_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Groupe requis pour créer un événement (assignez un groupe à l'utilisateur ou choisissez-en un).",
            )

    return await crud.create_event(payload, current_user.id, db)

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
    
    # Lecture: admin, owner, ou visibilité par groupe
    if current_user.role != UserRole.ADMIN and current_user.id != owner.id:
        slugs = visible_group_slugs_for_user(current_user)
        if not slugs:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        res = await db.execute(select(Group.id).where(Group.slug.in_(slugs)))
        visible_ids = {row[0] for row in res.all()}
        if not (event.group_id and event.group_id in visible_ids):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
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
    Vérifie que l'utilisateur a la permission.

    Spécification (08/01/2026): la modification des événements passés est autorisée pour tout le monde.
    """
    existing_event = await crud.get_event(event_id, db)
    
    owner = await crud.get_event_owner(existing_event, db)
    if not (current_user.role == UserRole.ADMIN or current_user.id == owner.id or can_manage_all_events(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Changement de groupe: uniquement ADMIN / chef de projet.
    update_data = event.model_dump(exclude_unset=True)
    if "group_id" in update_data:
        if update_data["group_id"] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Groupe requis: impossible de retirer le groupe d'un événement.",
            )
        if not can_assign_events_to_any_group(current_user) and update_data["group_id"] != existing_event.group_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return await crud.update_event(event_id, event, db)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprimer un événement (soft delete).
    Vérifie que l'utilisateur a la permission.

    Suppression: plus restrictive que la modification.
    - Événement passé: suppression réservée à l'ADMIN
    - Sinon: owner / ADMIN / rôles avec gestion globale
    """
    existing_event = await crud.get_event(event_id, db)

    # Past event deletion policy: ADMIN only
    try:
        start_raw = existing_event.start
        if isinstance(start_raw, str):
            if start_raw.endswith("Z"):
                start_raw = start_raw.replace("Z", "+00:00")
            start_dt = datetime.fromisoformat(start_raw)
            if start_dt.tzinfo is not None:
                start_dt = start_dt.replace(tzinfo=None)
        else:
            start_dt = datetime.fromisoformat(str(start_raw))
    except Exception:
        start_dt = None

    if start_dt is not None and start_dt < datetime.utcnow() and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    owner = await crud.get_event_owner(existing_event, db)
    if not (current_user.role == UserRole.ADMIN or current_user.id == owner.id or can_manage_all_events(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    await crud.delete_event(event_id, db)
    return None
