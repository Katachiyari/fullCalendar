from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CalendarEventRead(BaseModel):
    id: str
    project_id: Optional[str] = None
    owner_id: Optional[str] = None
    title: str
    start: datetime
    end: Optional[datetime] = None
    all_day: bool
    event_type: str
    severity: Optional[str] = None
    resources: List[str] = []
    rrule: Optional[str] = None

    class Config:
        from_attributes = True


class CalendarEventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    project_id: Optional[str] = None
    owner_id: Optional[str] = None
    start: datetime
    end: Optional[datetime] = None
    all_day: bool = False
    event_type: str = "MAINTENANCE"
    severity: Optional[str] = None
    resources: List[str] = Field(default_factory=list)
    rrule: Optional[str] = None


class CalendarEventPatch(BaseModel):
    title: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    all_day: Optional[bool] = None
    project_id: Optional[str] = None
    owner_id: Optional[str] = None
    severity: Optional[str] = None
    resources: Optional[List[str]] = None
    rrule: Optional[str] = None
