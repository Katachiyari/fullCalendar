from __future__ import annotations

import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import MonitoredServer, User
from app.dependencies import require_admin
from app.services.server_monitor import MonitorTarget, collect_remote_metrics


router = APIRouter(prefix="/admin", tags=["admin"])


class ServerTargetCreate(BaseModel):
    host: str = Field(..., min_length=1, max_length=255)
    name: str | None = Field(default=None, max_length=100)
    ssh_port: int = Field(default=22, ge=1, le=65535)
    disk_path: str = Field(default="/", max_length=255)


class ServerTargetRead(BaseModel):
    id: str
    host: str
    name: str | None = None
    ssh_port: int
    disk_path: str

    class Config:
        from_attributes = True


def _read_meminfo_bytes() -> tuple[int | None, int | None, int | None]:
    """Retourne (total, used, available) en bytes si possible."""
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            data = f.read().splitlines()
        values = {}
        for line in data:
            if ":" not in line:
                continue
            key, rest = line.split(":", 1)
            parts = rest.strip().split()
            if not parts:
                continue
            # /proc/meminfo est en kB
            values[key] = int(parts[0]) * 1024
        total = values.get("MemTotal")
        available = values.get("MemAvailable")
        if total is None or available is None:
            return None, None, None
        used = total - available
        return total, used, available
    except Exception:
        return None, None, None


@router.get("/server-metrics")
async def server_metrics(
    current_user: User = Depends(require_admin),
):
    uploads_path = os.getenv("UPLOADS_PATH", "/data/uploads")

    cpu_cores = os.cpu_count() or 0
    try:
        load_1, load_5, load_15 = os.getloadavg()
    except Exception:
        load_1 = load_5 = load_15 = 0.0

    mem_total, mem_used, mem_available = _read_meminfo_bytes()

    disk_total = disk_used = disk_free = None
    try:
        usage = shutil.disk_usage(uploads_path)
        disk_total, disk_used, disk_free = usage.total, usage.used, usage.free
    except Exception:
        pass

    return {
        "cpu": {
            "cores": cpu_cores,
            "load": {"avg_1": load_1, "avg_5": load_5, "avg_15": load_15},
        },
        "memory": {
            "total_bytes": mem_total,
            "used_bytes": mem_used,
            "available_bytes": mem_available,
        },
        "storage": {
            "path": uploads_path,
            "total_bytes": disk_total,
            "used_bytes": disk_used,
            "free_bytes": disk_free,
        },
    }


@router.get("/servers", response_model=list[ServerTargetRead])
async def list_servers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    res = await db.execute(select(MonitoredServer).order_by(MonitoredServer.created_at.desc()))
    return list(res.scalars().all())


@router.post("/servers", response_model=ServerTargetRead, status_code=status.HTTP_201_CREATED)
async def create_server(
    payload: ServerTargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    row = MonitoredServer(host=payload.host.strip(), name=(payload.name.strip() if payload.name else None), ssh_port=payload.ssh_port, disk_path=payload.disk_path)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    res = await db.execute(select(MonitoredServer).where(MonitoredServer.id == server_id))
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await db.delete(row)
    await db.commit()
    return None


@router.get("/servers/{server_id}/metrics")
async def get_server_metrics(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    res = await db.execute(select(MonitoredServer).where(MonitoredServer.id == server_id))
    row = res.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    ssh_user = os.getenv("OPSHUB_SSH_USER")
    ssh_key_path = os.getenv("OPSHUB_SSH_KEY_PATH")
    target = MonitorTarget(host=row.host, ssh_port=row.ssh_port or 22, disk_path=row.disk_path or "/")
    return await collect_remote_metrics(target, ssh_user=ssh_user, ssh_key_path=ssh_key_path)
