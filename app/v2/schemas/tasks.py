from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TaskRead(BaseModel):
    id: str
    project_id: str
    sprint_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    estimate_hours: Optional[float] = None
    due_at: Optional[datetime] = None
    position: int = 0
    gitlab_mr_url: Optional[str] = None
    gitlab_job_url: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    project_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    sprint_id: Optional[str] = None
    priority: str = Field(default="P3")
    estimate_hours: Optional[float] = Field(default=None, ge=0)
    due_at: Optional[datetime] = None
    gitlab_mr_url: Optional[str] = None
    gitlab_job_url: Optional[str] = None


class TaskPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimate_hours: Optional[float] = Field(default=None, ge=0)
    due_at: Optional[datetime] = None
    position: Optional[int] = None


class TaskCommentRead(BaseModel):
    id: str
    task_id: str
    user_id: str
    body: str
    mentions: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)
