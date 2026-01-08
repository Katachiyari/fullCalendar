"""Opérations CRUD pour l'authentification"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models import User, UserRole
from app.schemas_auth import RegisterRequest, UserResponse
from app.security import hash_password, verify_password


async def register_user(user_data: RegisterRequest, db: AsyncSession) -> User:
    """Créer un nouvel utilisateur (inscription)"""
    # Vérifier si l'email existe déjà
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Créer l'utilisateur
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        age=user_data.age,
        job_title=user_data.job_title,
        hashed_password=hash_password(user_data.password),
        role=UserRole.USER,  # Role par défaut
        is_active=True
    )
    
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


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    """Authentifier un utilisateur (login)"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password incorrect"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password incorrect"
        )
    
    return user


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """Récupérer un utilisateur par email"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


async def update_password(user_id: str, old_password: str, new_password: str, db: AsyncSession) -> User:
    """Mettre à jour le mot de passe d'un utilisateur"""
    from crud_user import get_user
    user = await get_user(user_id, db)
    
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    user.hashed_password = hash_password(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user
