from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_editor, require_viewer
from app.models import Task, TaskStatus, Priority, User
from app.v2.schemas.tasks import TaskRead, TaskCreate, TaskPatch
from app.v2.services.audit import write_audit

router = APIRouter(prefix="/v2/tasks", tags=["v2-tasks"])


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    limit: int = 200,
    project_id: str | None = None,
    sprint_id: str | None = None,
    status_: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    q = select(Task).order_by(Task.status, Task.position.asc(), Task.created_at.desc()).limit(limit)
    if project_id:
        q = q.where(Task.project_id == project_id)
    if sprint_id:
        q = q.where(Task.sprint_id == sprint_id)
    if status_:
        q = q.where(Task.status == TaskStatus(status_))

    res = await db.execute(q)
    return list(res.scalars().all())


@router.get("/today", response_model=list[TaskRead])
async def tasks_today(
    limit: int = 8,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today_start + timedelta(days=1)

    q = (
        select(Task)
        .where(Task.due_at.is_not(None))
        .where(Task.due_at >= today_start)
        .where(Task.due_at < tomorrow)
        .order_by(Task.due_at.asc())
        .limit(limit)
    )
    res = await db.execute(q)
    rows = list(res.scalars().all())
    if rows:
        return rows

    # Fallback (démo/dev): si rien n'est dû aujourd'hui, renvoyer des tâches récentes
    q2 = (
        select(Task)
        .where(Task.status != TaskStatus.DONE)
        .order_by(Task.updated_at.desc(), Task.created_at.desc())
        .limit(limit)
    )
    res2 = await db.execute(q2)
    return list(res2.scalars().all())


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    # position = max(position)+1 within status
    max_pos = await db.execute(select(func.max(Task.position)).where(Task.project_id == payload.project_id))
    pos = (max_pos.scalar_one_or_none() or 0) + 1

    task = Task(
        project_id=payload.project_id,
        sprint_id=payload.sprint_id,
        title=payload.title,
        description=payload.description,
        status=TaskStatus.TODO,
        priority=Priority(payload.priority),
        estimate_hours=payload.estimate_hours,
        due_at=payload.due_at,
        position=pos,
        gitlab_mr_url=payload.gitlab_mr_url,
        gitlab_job_url=payload.gitlab_job_url,
        created_by=current_user.id,
        updated_at=datetime.utcnow(),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    await write_audit(db, current_user, "task.create", "task", task.id, before=None, after={"title": task.title})
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def patch_task(
    task_id: str,
    payload: TaskPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    res = await db.execute(select(Task).where(Task.id == task_id))
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    before = {"status": task.status.value, "priority": task.priority.value, "title": task.title}

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        task.status = TaskStatus(data["status"])
    if "priority" in data and data["priority"] is not None:
        task.priority = Priority(data["priority"])
    for k in ("title", "description", "estimate_hours", "due_at", "position"):
        if k in data:
            setattr(task, k, data[k])

    task.updated_at = datetime.utcnow()
    db.add(task)
    await db.commit()
    await db.refresh(task)

    after = {"status": task.status.value, "priority": task.priority.value, "title": task.title}
    await write_audit(db, current_user, "task.update", "task", task.id, before=before, after=after)

    return task
