from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models import Group
from app.schemas_groups import GroupCreate, GroupUpdate


async def list_groups(db: AsyncSession):
    result = await db.execute(select(Group).order_by(Group.name))
    return result.scalars().all()


async def get_group(group_id: str, db: AsyncSession) -> Group:
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


async def get_group_by_slug(slug: str, db: AsyncSession) -> Group | None:
    result = await db.execute(select(Group).where(Group.slug == slug))
    return result.scalar_one_or_none()


async def create_group(group_in: GroupCreate, db: AsyncSession) -> Group:
    group = Group(**group_in.model_dump())
    db.add(group)
    try:
        await db.commit()
        await db.refresh(group)
        return group
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Group already exists")


async def update_group(group_id: str, group_in: GroupUpdate, db: AsyncSession) -> Group:
    group = await get_group(group_id, db)
    update_data = group_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)
    db.add(group)
    try:
        await db.commit()
        await db.refresh(group)
        return group
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Group already exists")


async def delete_group(group_id: str, db: AsyncSession) -> None:
    group = await get_group(group_id, db)
    await db.delete(group)
    await db.commit()
