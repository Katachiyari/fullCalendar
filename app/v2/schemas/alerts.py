from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    project_id: Optional[str] = None
    title: str = Field(..., min_length=2, max_length=200)
    severity: str = Field(default="P3")
    source: str = Field(default="MANUAL")
    payload: Optional[dict] = None


class AlertRead(BaseModel):
    id: str
    project_id: Optional[str] = None
    title: str
    severity: str
    status: str
    source: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertResolve(BaseModel):
    resolution_note: Optional[str] = Field(default=None, max_length=2000)


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    severity: Optional[str] = Field(default=None)
    # Stored inside Alert.payload to avoid schema migrations
    workflow_status: Optional[str] = Field(default=None, max_length=30)  # OPEN/IN_PROGRESS
    assigned_to: Optional[str] = Field(default=None, max_length=200)  # email or user id
    note: Optional[str] = Field(default=None, max_length=2000)
