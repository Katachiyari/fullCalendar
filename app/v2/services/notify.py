from __future__ import annotations

import os
from typing import Iterable
import httpx

from app.notifications import send_email


def _severity_rank(sev: str) -> int:
    return {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(sev, 3)


async def notify_slack(message: str) -> None:
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json={"text": message})


async def notify_email(recipients: Iterable[str], subject: str, body: str) -> None:
    for r in recipients:
        send_email(r, subject, body)


async def notify_escalation(
    severity: str,
    assigned_emails: Iterable[str],
    admin_emails: Iterable[str],
    message: str,
) -> None:
    # P0 -> tous (admins + assignés), P3 -> assigné (simple)
    sev = severity or "P3"
    if _severity_rank(sev) <= 0:
        recipients = sorted(set(list(assigned_emails) + list(admin_emails)))
    else:
        recipients = sorted(set(list(assigned_emails)))

    await notify_slack(message)
    if recipients:
        await notify_email(recipients, f"[OpsHub] {sev} notification", message)
