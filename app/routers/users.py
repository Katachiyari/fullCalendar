from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models import User, UserRole
from app.schemas_user import UserCreate, UserRead, UserUpdate
import app.crud_user as crud_user
from app.dependencies import get_current_user, require_admin


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Créer un nouvel utilisateur (ADMIN seulement).
    """
    return await crud_user.create_user(user, db)


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Lister tous les utilisateurs (ADMIN seulement).
    """
    return await crud_user.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Récupérer un utilisateur par son ID (ADMIN seulement).
    """
    return await crud_user.get_user(user_id, db)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Mettre à jour un utilisateur (ADMIN seulement).
    """
    return await crud_user.update_user(user_id, user_update, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Supprimer un utilisateur (ADMIN seulement).
    Empêche la suppression du dernier administrateur.
    """
    # Charger l'utilisateur à supprimer
    user_to_delete = await crud_user.get_user(user_id, db)
    
    # Si c'est un ADMIN, vérifier qu'il n'est pas le dernier
    if user_to_delete.role == UserRole.ADMIN:
        admin_count = await crud_user.count_admins(db)
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete the last admin user"
            )
    
    await crud_user.delete_user(user_id, db)
    return None
