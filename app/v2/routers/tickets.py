from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_viewer
from app.models import Alert, AlertSource, AlertStatus, Priority, User
from app.v2.schemas.alerts import AlertCreate, AlertRead, AlertResolve, TicketUpdate
from app.v2.services.audit import write_audit

# Tickets internes simples: on réutilise le modèle v2 "Alert" comme base.
router = APIRouter(prefix="/v2/tickets", tags=["v2-tickets"])


@router.get("", response_model=list[AlertRead])
async def list_tickets(
    limit: int = 20,
    status_: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    q = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    if status_:
        q = q.where(Alert.status == AlertStatus(status_))
    res = await db.execute(q)
    return list(res.scalars().all())


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    ticket = Alert(
        project_id=payload.project_id,
        title=payload.title,
        severity=Priority(payload.severity),
        status=AlertStatus.OPEN,
        source=AlertSource(payload.source),
        payload=payload.payload,
        created_at=datetime.utcnow(),
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    await write_audit(
        db,
        current_user,
        "ticket.create",
        "ticket",
        ticket.id,
        before=None,
        after={"title": ticket.title, "severity": ticket.severity.value, "status": ticket.status.value},
    )

    return ticket


@router.post("/{ticket_id}/resolve", response_model=AlertRead)
async def resolve_ticket(
    ticket_id: str,
    payload: AlertResolve,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    res = await db.execute(select(Alert).where(Alert.id == ticket_id))
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if ticket.status == AlertStatus.RESOLVED:
        return ticket

    before = {"status": ticket.status.value}
    ticket.status = AlertStatus.RESOLVED
    ticket.resolved_at = datetime.utcnow()
    ticket.resolved_by = current_user.id

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    await write_audit(
        db,
        current_user,
        "ticket.resolve",
        "ticket",
        ticket.id,
        before=before,
        after={"status": ticket.status.value, "resolution_note": payload.resolution_note},
    )

    return ticket


@router.patch("/{ticket_id}", response_model=AlertRead)
async def update_ticket(
    ticket_id: str,
    payload: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    res = await db.execute(select(Alert).where(Alert.id == ticket_id))
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    before = {
        "title": ticket.title,
        "severity": ticket.severity.value,
        "status": ticket.status.value,
        "payload": ticket.payload,
    }

    update = payload.model_dump(exclude_unset=True)
    if "title" in update and update["title"] is not None:
        ticket.title = update["title"]
    if "severity" in update and update["severity"] is not None:
        ticket.severity = Priority(update["severity"])

    # Store ticketing metadata in payload JSON (no DB migration)
    meta = dict(ticket.payload or {})
    if "workflow_status" in update:
        meta["workflow_status"] = update.get("workflow_status")
    if "assigned_to" in update:
        meta["assigned_to"] = update.get("assigned_to")

    # Append a lightweight history entry
    history = list(meta.get("history") or [])
    history.append(
        {
            "at": datetime.utcnow().isoformat(),
            "actor_id": current_user.id,
            "action": "ticket.update",
            "note": update.get("note"),
            "changes": {k: v for k, v in update.items() if k != "note"},
        }
    )
    meta["history"] = history[-50:]
    ticket.payload = meta

    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)

    await write_audit(
        db,
        current_user,
        "ticket.update",
        "ticket",
        ticket.id,
        before=before,
        after={
            "title": ticket.title,
            "severity": ticket.severity.value,
            "status": ticket.status.value,
            "payload": ticket.payload,
        },
    )

    return ticket
