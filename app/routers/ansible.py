from __future__ import annotations

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status

from app.models import User
from app.dependencies import get_current_user


router = APIRouter(prefix="/ansible", tags=["ansible"])


def _resolve_under_uploads(path_str: str) -> Path:
    uploads_root = Path(os.getenv("UPLOADS_PATH", "/data/uploads")).resolve()
    p = Path(path_str).expanduser()
    if not p.is_absolute():
        p = (uploads_root / p).resolve()
    else:
        p = p.resolve()

    try:
        p.relative_to(uploads_root)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Path must be under uploads root",
        )
    return p


def _find_inventory_file(p: Path) -> Path:
    if p.is_file():
        return p
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")

    candidates = [p / "inventory.ini", p / "hosts.ini", p / "hosts"]
    for c in candidates:
        if c.exists() and c.is_file():
            return c

    # fallback: first .ini file
    for c in sorted(p.glob("*.ini")):
        if c.is_file():
            return c

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No inventory file found")


def _parse_inventory_ini(content: str):
    groups: dict[str, list[str]] = {}
    current_group: str | None = None

    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue

        if line.startswith("[") and line.endswith("]"):
            current_group = line[1:-1].strip()
            groups.setdefault(current_group, [])
            continue

        if current_group is None:
            groups.setdefault("ungrouped", []).append(line)
            continue

        groups.setdefault(current_group, []).append(line)

    # Simplification: extraire les hôtes (premier token) et ansible_host si présent
    parsed = []
    for group, lines in groups.items():
        hosts = []
        for host_line in lines:
            if host_line.startswith("["):
                continue
            parts = host_line.split()
            if not parts:
                continue
            host = parts[0]
            ip = None
            for part in parts[1:]:
                if part.startswith("ansible_host="):
                    ip = part.split("=", 1)[1]
                    break
            hosts.append({"name": host, "ip": ip})
        parsed.append({"group": group, "hosts": hosts})

    return parsed


@router.post("/analyze")
async def analyze_inventory(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    # Accessible à tout utilisateur authentifié (les droits fins peuvent être ajoutés)
    path = payload.get("path")
    if not path:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="path is required")

    target = _resolve_under_uploads(str(path))
    inv_file = _find_inventory_file(target)
    try:
        content = inv_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot read inventory")

    return {
        "inventory_file": str(inv_file),
        "groups": _parse_inventory_ini(content),
    }
