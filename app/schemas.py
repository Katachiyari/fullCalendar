from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
from datetime import date as date_type

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start: str
    end: Optional[str] = None
    color: str = "#28a745"
    resources: List[str] = Field(default_factory=list)
    rrule: Optional[str] = None
    all_day: bool = False

    @field_validator('start')
    @classmethod
    def validate_start_not_past(cls, v):
        """Vérifier que start est au minimum dans 15 minutes"""
        if not v:
            return v
            
        try:
            # Parser la date sans timezone
            if isinstance(v, str):
                # Gérer plusieurs formats: "2026-01-10T10:00:00" ou "2026-01-10T10:00:00+00:00"
                if '+' in v or v.endswith('Z'):
                    v_clean = v.replace('Z', '+00:00')
                    start_dt = datetime.fromisoformat(v_clean)
                    # Enlever la timezone pour comparaison cohérente
                    start_dt = start_dt.replace(tzinfo=None)
                else:
                    # Accepter aussi le format date-only (YYYY-MM-DD) pour les événements all-day
                    if len(v) == 10:
                        d = date_type.fromisoformat(v)
                        start_dt = datetime(d.year, d.month, d.day)
                    else:
                        start_dt = datetime.fromisoformat(v)
            else:
                start_dt = v if isinstance(v, datetime) else datetime.fromisoformat(str(v))
                if start_dt.tzinfo:
                    start_dt = start_dt.replace(tzinfo=None)
            
            # Vérifier que c'est au moins dans 15 min
            now = datetime.utcnow()
            min_start = now + timedelta(minutes=15)
            
            # if start_dt < min_start:
            #    raise ValueError('La date doit être au minimum dans 15 minutes')
        except ValueError as e:
            if 'La date doit être' in str(e):
                raise
            raise ValueError(f'Format de date invalide: {v}')
        return v

class EventCreate(EventBase):
    # owner_id sera ajouté automatiquement par le endpoint
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    color: Optional[str] = None
    resources: Optional[List[str]] = None
    rrule: Optional[str] = None
    all_day: Optional[bool] = None

    @field_validator('start')
    @classmethod
    def validate_start_not_past(cls, v):
        """Vérifier que start est au minimum dans 15 minutes (optionnel pour update)"""
        if v is None:
            return v
        try:
            if isinstance(v, str):
                if '+' in v or v.endswith('Z'):
                    v_clean = v.replace('Z', '+00:00')
                    start_dt = datetime.fromisoformat(v_clean)
                    start_dt = start_dt.replace(tzinfo=None)
                else:
                    if len(v) == 10:
                        d = date_type.fromisoformat(v)
                        start_dt = datetime(d.year, d.month, d.day)
                    else:
                        start_dt = datetime.fromisoformat(v)
            else:
                start_dt = v if isinstance(v, datetime) else datetime.fromisoformat(str(v))
                if start_dt.tzinfo:
                    start_dt = start_dt.replace(tzinfo=None)
            
            now = datetime.utcnow()
            min_start = now + timedelta(minutes=15)
            if start_dt < min_start:
                raise ValueError('La date doit être au minimum dans 15 minutes')
        except ValueError as e:
            if 'La date doit être' in str(e):
                raise
        return v

class Event(EventBase):
    id: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True
