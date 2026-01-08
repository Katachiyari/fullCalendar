"""Schémas pour l'authentification"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """Réponse avec token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class LoginRequest(BaseModel):
    """Requête de connexion"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Requête d'inscription"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=120)
    job_title: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Changement de mot de passe"""
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """Réponse utilisateur (sans mot de passe)"""
    id: str
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    age: Optional[int]
    job_title: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
