from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
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
    group_id: Optional[str] = None

class EventCreate(EventBase):
    # owner_id sera ajouté automatiquement par le endpoint

    @field_validator('start')
    @classmethod
    def validate_start_format(cls, v):
        """Vérifier uniquement le format de date (création).

        Le cahier des charges (janvier 2026) demande d'autoriser les événements passés.
        """
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
        except ValueError as e:
            raise ValueError(f'Format de date invalide: {v}')
        return v

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    color: Optional[str] = None
    resources: Optional[List[str]] = None
    rrule: Optional[str] = None
    all_day: Optional[bool] = None
    group_id: Optional[str] = None

    # NOTE: Le cahier des charges (janvier 2026) demande d'autoriser la modification
    # des événements passés pour tout le monde. Aucune contrainte temporelle ici.

class Event(EventBase):
    id: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True
