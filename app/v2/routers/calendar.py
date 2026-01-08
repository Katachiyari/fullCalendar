from __future__ import annotations

from datetime import datetime
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_viewer, require_editor
from app.models import CalendarEntry, CalendarEventType, Priority, User
from app.v2.schemas.calendar import CalendarEventRead, CalendarEventCreate, CalendarEventPatch
from app.v2.services.audit import write_audit

router = APIRouter(prefix="/v2/calendar", tags=["v2-calendar"])


def _overlaps(a_start: datetime, a_end: datetime | None, b_start: datetime, b_end: datetime | None) -> bool:
    ae = a_end or a_start
    be = b_end or b_start
    return a_start < be and b_start < ae


def _resource_overlap(resources_a: Iterable[str], resources_b: Iterable[str]) -> bool:
    sa = {r for r in resources_a if r}
    sb = {r for r in resources_b if r}
    return bool(sa.intersection(sb))


@router.get("/events", response_model=list[CalendarEventRead])
async def list_calendar_events(
    limit: int = 200,
    project_id: str | None = None,
    severity: str | None = None,
    owner_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    q = select(CalendarEntry).order_by(CalendarEntry.start.asc()).limit(limit)
    if project_id:
        q = q.where(CalendarEntry.project_id == project_id)
    if severity:
        try:
            sev = Priority(severity)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        q = q.where(CalendarEntry.severity == sev)
    if owner_id:
        q = q.where(CalendarEntry.owner_id == owner_id)

    res = await db.execute(q)
    return list(res.scalars().all())


@router.post("/events", response_model=CalendarEventRead, status_code=status.HTTP_201_CREATED)
async def create_calendar_event(
    payload: CalendarEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    try:
        event_type = CalendarEventType(payload.event_type) if payload.event_type else CalendarEventType.MAINTENANCE
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    severity = None
    if payload.severity:
        try:
            severity = Priority(payload.severity)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # conflict detection: only for same resources
    if payload.resources:
        res = await db.execute(select(CalendarEntry).order_by(CalendarEntry.start.asc()))
        for e in res.scalars().all():
            if e.resources and _resource_overlap(payload.resources, e.resources):
                if _overlaps(payload.start, payload.end, e.start, e.end):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resource conflict (overlap)")

    entry = CalendarEntry(
        title=payload.title,
        project_id=payload.project_id,
        owner_id=payload.owner_id,
        start=payload.start,
        end=payload.end,
        all_day=payload.all_day,
        event_type=event_type,
        severity=severity,
        resources=payload.resources,
        rrule=payload.rrule,
        updated_at=datetime.utcnow(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    await write_audit(db, current_user, "calendar.create", "calendar_entry", entry.id, after={"title": entry.title})
    return entry


@router.patch("/events/{event_id}", response_model=CalendarEventRead)
async def patch_calendar_event(
    event_id: str,
    payload: CalendarEventPatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    res = await db.execute(select(CalendarEntry).where(CalendarEntry.id == event_id))
    entry = res.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    before = {"start": entry.start.isoformat(), "end": (entry.end.isoformat() if entry.end else None)}

    data = payload.model_dump(exclude_unset=True)
    for k in ("title", "start", "end", "all_day", "project_id", "owner_id", "rrule"):
        if k in data:
            setattr(entry, k, data[k])
    if "severity" in data:
        if data["severity"]:
            try:
                entry.severity = Priority(data["severity"])
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        else:
            entry.severity = None
    if "resources" in data and data["resources"] is not None:
        entry.resources = data["resources"]

    # conflict detection
    if entry.resources:
        res2 = await db.execute(select(CalendarEntry).where(CalendarEntry.id != entry.id))
        for e in res2.scalars().all():
            if e.resources and _resource_overlap(entry.resources, e.resources):
                if _overlaps(entry.start, entry.end, e.start, e.end):
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resource conflict (overlap)")

    entry.updated_at = datetime.utcnow()
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    after = {"start": entry.start.isoformat(), "end": (entry.end.isoformat() if entry.end else None)}
    await write_audit(db, current_user, "calendar.update", "calendar_entry", entry.id, before=before, after=after)

    return entry
