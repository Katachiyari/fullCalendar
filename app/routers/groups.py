from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models import User
from app.dependencies import get_current_user, require_admin
from app.schemas_groups import GroupCreate, GroupRead, GroupUpdate
import app.crud_groups as crud_groups
from app.v2.services.audit import write_audit


router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=List[GroupRead])
async def list_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_groups.list_groups(db)


@router.post("/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(
    group: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    created = await crud_groups.create_group(group, db)
    await write_audit(db, current_user, "admin.group.create", "group", created.id, before=None, after={"name": created.name, "slug": created.slug})
    return created


@router.put("/{group_id}", response_model=GroupRead)
async def update_group(
    group_id: str,
    group: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing = await crud_groups.get_group(group_id, db)
    before = {"name": existing.name, "slug": existing.slug}
    updated = await crud_groups.update_group(group_id, group, db)
    after = {"name": updated.name, "slug": updated.slug}
    await write_audit(db, current_user, "admin.group.update", "group", group_id, before=before, after=after)
    return updated


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing = await crud_groups.get_group(group_id, db)
    before = {"name": existing.name, "slug": existing.slug}
    await crud_groups.delete_group(group_id, db)
    await write_audit(db, current_user, "admin.group.delete", "group", group_id, before=before, after=None)
    return None
