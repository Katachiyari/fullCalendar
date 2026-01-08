from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.models import User, UserRole
from app.schemas_user import UserCreateAdmin, UserRead, UserUpdate, AdminSetPassword
import app.crud_user as crud_user
from app.dependencies import get_current_user, require_admin
from app.v2.services.audit import write_audit


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreateAdmin,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Créer un nouvel utilisateur (ADMIN seulement).
    """
    created = await crud_user.create_user_admin(user, db)
    await write_audit(
        db,
        current_user,
        "admin.user.create",
        "user",
        created.id,
        before=None,
        after={"email": created.email, "role": created.role.value},
    )
    return created


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
    existing = await crud_user.get_user(user_id, db)
    before = {
        "email": existing.email,
        "first_name": existing.first_name,
        "last_name": existing.last_name,
        "role": existing.role.value,
        "is_active": existing.is_active,
        "email_verified": getattr(existing, "email_verified", True),
        "group_id": getattr(existing, "group_id", None),
    }
    updated = await crud_user.update_user(user_id, user_update, db)
    after = {
        "email": updated.email,
        "first_name": updated.first_name,
        "last_name": updated.last_name,
        "role": updated.role.value,
        "is_active": updated.is_active,
        "email_verified": getattr(updated, "email_verified", True),
        "group_id": getattr(updated, "group_id", None),
    }
    await write_audit(db, current_user, "admin.user.update", "user", updated.id, before=before, after=after)
    return updated


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
    
    before = {"email": user_to_delete.email, "role": user_to_delete.role.value}
    await crud_user.delete_user(user_id, db)
    await write_audit(db, current_user, "admin.user.delete", "user", user_id, before=before, after=None)
    return None


@router.put("/{user_id}/password", response_model=UserRead)
async def admin_set_password(
    user_id: str,
    payload: AdminSetPassword,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Changer le mot de passe d'un utilisateur (ADMIN seulement)."""
    updated = await crud_user.set_user_password(user_id, payload.new_password, db)
    await write_audit(
        db,
        current_user,
        "admin.user.set_password",
        "user",
        user_id,
        before=None,
        after={"email": updated.email},
    )
    return updated
