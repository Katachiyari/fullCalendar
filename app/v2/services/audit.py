from __future__ import annotations

from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog, User


async def write_audit(
    db: AsyncSession,
    actor: Optional[User],
    action: str,
    entity_type: str,
    entity_id: str,
    before: Any = None,
    after: Any = None,
) -> None:
    entry = AuditLog(
        actor_id=(actor.id if actor else None),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
    )
    db.add(entry)
    await db.commit()
