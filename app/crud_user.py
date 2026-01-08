from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import uuid
from app.models import User, UserRole
from app.schemas_user import UserCreate, UserCreateAdmin, UserUpdate
from app.security import hash_password
import app.crud_groups as crud_groups


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Récupérer tous les utilisateurs"""
    stmt = (
        select(User)
        .options(selectinload(User.group))
        .order_by(User.created_at)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_user(user_id: str, db: AsyncSession):
    """Récupérer un utilisateur par son ID"""
    result = await db.execute(
        select(User).options(selectinload(User.group)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user


async def get_user_by_email(email: str, db: AsyncSession):
    """Récupérer un utilisateur par son email"""
    result = await db.execute(
        select(User).options(selectinload(User.group)).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def create_user(user_in: UserCreate, db: AsyncSession):
    """Créer un nouvel utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = await get_user_by_email(user_in.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Création sans mot de passe n'est pas utilisable pour l'authentification.
    # On conserve la fonction pour compat, mais on force un mot de passe inutilisable.
    user_data = user_in.model_dump()
    user_data["hashed_password"] = hash_password(str(uuid.uuid4()))
    user = User(**user_data)
    db.add(user)
    
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


async def create_user_admin(user_in: UserCreateAdmin, db: AsyncSession):
    """Créer un utilisateur (ADMIN) avec mot de passe hashé."""
    existing_user = await get_user_by_email(user_in.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hash_password(user_in.password)
    # Un utilisateur créé par admin est considéré vérifié par défaut (évite blocage)
    user_data.setdefault("email_verified", True)
    
    # Si aucun groupe n'est fourni, on affecte un groupe par défaut (meilleur UX / cohérence avec le calendrier).
    if user_data.get("group_id") in (None, ""):
        default_group = await crud_groups.get_group_by_slug("developpeur", db)
        if default_group:
            user_data["group_id"] = default_group.id
    user = User(**user_data)
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


async def update_user(user_id: str, user_in: UserUpdate, db: AsyncSession):
    """Mettre à jour un utilisateur"""
    user = await get_user(user_id, db)
    
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Si l'email est modifié, vérifier qu'il n'existe pas déjà
    if "email" in update_data and update_data["email"] != user.email:
        existing_user = await get_user_by_email(update_data["email"], db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


async def delete_user(user_id: str, db: AsyncSession):
    """Supprimer un utilisateur"""
    user = await get_user(user_id, db)
    await db.delete(user)
    await db.commit()
    return user


async def count_admins(db: AsyncSession) -> int:
    """Compter le nombre d'administrateurs"""
    stmt = select(User).where(User.role == UserRole.ADMIN)
    result = await db.execute(stmt)
    return len(result.scalars().all())


async def set_user_password(user_id: str, new_password: str, db: AsyncSession) -> User:
    user = await get_user(user_id, db)
    user.hashed_password = hash_password(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
