from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from app.models import UserRole
from app.schemas_groups import GroupRead


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    job_title: Optional[str] = Field(None, max_length=200)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.USER
    theme: str = Field(default="midnight", max_length=64)
    group_id: Optional[str] = None


class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur"""
    pass


class UserCreateAdmin(UserBase):
    """Schéma pour la création d'un utilisateur par un ADMIN"""
    password: str = Field(..., min_length=8, max_length=200)


class UserRead(UserBase):
    """Schéma pour la lecture d'un utilisateur"""
    id: str
    created_at: datetime
    is_active: bool = True
    email_verified: bool = True
    group: Optional[GroupRead] = None

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
    is_active: Optional[bool] = None
    theme: Optional[str] = Field(None, max_length=64)
    group_id: Optional[str] = None
    email_verified: Optional[bool] = None


class AdminSetPassword(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=200)
