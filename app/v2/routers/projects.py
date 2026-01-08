from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_viewer, require_editor
from app.models import Project, User
from app.v2.services.audit import write_audit

router = APIRouter(prefix="/v2/projects", tags=["v2-projects"])


@router.get("", response_model=list[dict])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    res = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "created_at": p.created_at,
        }
        for p in res.scalars().all()
    ]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_project(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="name is required")

    project = Project(name=name, description=payload.get("description"), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    db.add(project)
    await db.commit()
    await db.refresh(project)

    await write_audit(db, current_user, "project.create", "project", project.id, after={"name": project.name})

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
    }
