from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_viewer, require_editor
from app.models import Alert, AlertStatus, Priority, AlertSource, User
from app.v2.schemas.alerts import AlertRead, AlertResolve
from app.v2.services.audit import write_audit

router = APIRouter(prefix="/v2/alerts", tags=["v2-alerts"])


@router.get("", response_model=list[AlertRead])
async def list_alerts(
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


@router.post("/{alert_id}/resolve", response_model=AlertRead)
async def resolve_alert(
    alert_id: str,
    payload: AlertResolve,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    res = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = res.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    if alert.status == AlertStatus.RESOLVED:
        return alert

    before = {"status": alert.status.value}
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = __import__("datetime").datetime.utcnow()
    alert.resolved_by = current_user.id
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    await write_audit(db, current_user, "alert.resolve", "alert", alert.id, before=before, after={"status": alert.status.value})

    return alert
