from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_viewer, require_editor
from app.models import Sprint, User
from app.v2.services.audit import write_audit

router = APIRouter(prefix="/v2/sprints", tags=["v2-sprints"])


@router.get("", response_model=list[dict])
async def list_sprints(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    q = select(Sprint).order_by(Sprint.start_date.desc())
    if project_id:
        q = q.where(Sprint.project_id == project_id)

    res = await db.execute(q)
    return [
        {
            "id": s.id,
            "project_id": s.project_id,
            "name": s.name,
            "start_date": s.start_date,
            "end_date": s.end_date,
            "created_at": s.created_at,
        }
        for s in res.scalars().all()
    ]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_sprint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    name = (payload.get("name") or "").strip() or "Sprint"
    project_id = payload.get("project_id")
    if not project_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="project_id is required")

    start = payload.get("start_date")
    end = payload.get("end_date")

    # Accept either ISO strings or omit to auto-derive a 14-day sprint.
    if isinstance(start, str):
        start_date = date.fromisoformat(start)
    elif isinstance(start, date):
        start_date = start
    else:
        start_date = date.today()

    if isinstance(end, str):
        end_date = date.fromisoformat(end)
    elif isinstance(end, date):
        end_date = end
    else:
        end_date = start_date + timedelta(days=14)

    sprint = Sprint(
        project_id=project_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)

    await write_audit(db, current_user, "sprint.create", "sprint", sprint.id, after={"name": sprint.name})

    return {
        "id": sprint.id,
        "project_id": sprint.project_id,
        "name": sprint.name,
        "start_date": sprint.start_date,
        "end_date": sprint.end_date,
        "created_at": sprint.created_at,
    }
