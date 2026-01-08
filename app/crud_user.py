from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import User, UserRole
from app.schemas_user import UserCreate, UserUpdate


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Récupérer tous les utilisateurs"""
    stmt = select(User).order_by(User.created_at).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_user(user_id: str, db: AsyncSession):
    """Récupérer un utilisateur par son ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user


async def get_user_by_email(email: str, db: AsyncSession):
    """Récupérer un utilisateur par son email"""
    result = await db.execute(select(User).where(User.email == email))
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
    
    user = User(**user_in.model_dump())
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
