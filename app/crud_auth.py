"""Opérations CRUD pour l'authentification"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import uuid

from app.models import User, UserRole, EmailVerificationToken
from app.schemas_auth import RegisterRequest, UserResponse
from app.security import hash_password, verify_password
from app.notifications import send_email
import app.crud_groups as crud_groups


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
    # Assigner un groupe par défaut si disponible (métier simple)
    default_group = await crud_groups.get_group_by_slug("developpeur", db)

    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        age=user_data.age,
        job_title=user_data.job_title,
        hashed_password=hash_password(user_data.password),
        role=UserRole.USER,  # Role par défaut
        is_active=True,
        email_verified=True,
        group_id=(default_group.id if default_group else None),
        theme="midnight",
    )
    
    db.add(user)
    
    try:
        await db.commit()
        await db.refresh(user)

        # Important: éviter un lazy-load async lors de la sérialisation Pydantic
        # (UserResponse inclut `group`). On recharge l'utilisateur avec son group.
        result = await db.execute(
            select(User).options(selectinload(User.group)).where(User.id == user.id)
        )
        return result.scalar_one()
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


async def request_email_verification(user: User, db: AsyncSession) -> str:
    """Crée un token de vérification email et tente l'envoi."""
    if user.email_verified:
        return ""

    token_value = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=24)
    token = EmailVerificationToken(
        user_id=user.id,
        token=token_value,
        expires_at=expires_at,
    )
    db.add(token)
    await db.commit()

    # Envoi best-effort
    verification_url = f"/auth/verify-email?token={token_value}"
    body = (
        "Bonjour,\n\n"
        "Veuillez vérifier votre adresse email en ouvrant ce lien :\n"
        f"{verification_url}\n\n"
        "Ce lien expire dans 24 heures.\n"
    )
    send_email(user.email, "Vérification email OpsHub", body)

    return token_value


async def verify_email_token(token_value: str, db: AsyncSession) -> User:
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == token_value)
    )
    tok = result.scalar_one_or_none()
    if not tok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token")

    if tok.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already used")

    if tok.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    # Charger user
    result_u = await db.execute(select(User).where(User.id == tok.user_id))
    user = result_u.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.email_verified = True
    tok.used_at = datetime.utcnow()
    db.add(user)
    db.add(tok)
    await db.commit()
    await db.refresh(user)
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
