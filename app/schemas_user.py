from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from app.models import UserRole


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    job_title: Optional[str] = Field(None, max_length=200)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur"""
    pass


class UserRead(UserBase):
    """Schéma pour la lecture d'un utilisateur"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    job_title: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
