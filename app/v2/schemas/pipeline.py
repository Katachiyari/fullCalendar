from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PipelineStatus(BaseModel):
    status: str
    ref: Optional[str] = None
    url: Optional[str] = None
    updated_at: Optional[datetime] = None
