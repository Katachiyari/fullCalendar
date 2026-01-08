from __future__ import annotations

import os
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_viewer
from app.models import PipelineEvent, User
from app.v2.schemas.pipeline import PipelineStatus

router = APIRouter(prefix="/v2/pipeline", tags=["v2-pipeline"])


@router.get("/status", response_model=PipelineStatus)
async def pipeline_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    res = await db.execute(select(PipelineEvent).order_by(PipelineEvent.created_at.desc()).limit(1))
    ev = res.scalar_one_or_none()
    if not ev:
        return PipelineStatus(status="unknown")
    return PipelineStatus(status=ev.status, ref=ev.ref, url=ev.url, updated_at=ev.created_at)
