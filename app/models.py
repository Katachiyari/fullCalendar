from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """Enum pour les rôles utilisateur"""
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    job_title = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String)
    hashed_password = Column(String, nullable=False)  # ⭐ Nouveau
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True)  # ⭐ Nouveau
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec Event
    events = relationship("Event", back_populates="owner", lazy="dynamic")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    start = Column(String, nullable=False)
    end = Column(String)
    color = Column(String, default="#28a745")  # green default
    resources = Column(JSON, default=list)  # ["pod-01", "server-web"]
    rrule = Column(String)  # "FREQ=WEEKLY;BYDAY=MO"
    all_day = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec User
    owner = relationship("User", back_populates="events")
