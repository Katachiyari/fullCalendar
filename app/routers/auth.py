"""Routes d'authentification"""
from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import timedelta

from app.database import get_db
from app.models import User
from app.schemas_auth import (
    LoginRequest, RegisterRequest, TokenResponse, 
    ChangePasswordRequest, UserResponse
)
import app.crud_auth as crud_auth
from app.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, decode_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Créer un nouveau compte utilisateur"""
    user = await crud_auth.register_user(user_data, db)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Se connecter avec email et mot de passe"""
    user = await crud_auth.authenticate_user(credentials.email, credentials.password, db)
    
    # Créer le token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Récupérer les informations de l'utilisateur connecté"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_update: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour le profil utilisateur"""
    from crud_user import update_user as update_user_func
    from schemas_user import UserUpdate
    
    # Créer un objet UserUpdate à partir du dictionnaire
    update_data = UserUpdate(**user_update)
    
    updated_user = await update_user_func(current_user.id, update_data, db)
    return updated_user


@router.post("/change-password")
async def change_password(
    pwd_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Changer le mot de passe de l'utilisateur connecté"""
    await crud_auth.update_password(
        current_user.id,
        pwd_data.old_password,
        pwd_data.new_password,
        db
    )
    
    return {"message": "Password changed successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer son compte utilisateur"""
    from crud_user import delete_user
    await delete_user(current_user.id, db)
    return None


@router.post("/logout")
async def logout():
    """Déconnexion (côté client : supprimer le token)"""
    return {"message": "Logged out successfully"}
