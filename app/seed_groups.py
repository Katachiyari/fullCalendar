from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas_groups import GroupCreate
import app.crud_groups as crud_groups


DEFAULT_GROUPS: list[GroupCreate] = [
    GroupCreate(slug="chef_projet", name="Chef de projet", description="Accès complet aux calendriers (métier)."),
    GroupCreate(slug="developpeur", name="Développeur", description="Visibilité limitée aux développeurs."),
    GroupCreate(slug="devops", name="DevOps", description="Visibilité DevOps + Dev + Réseau."),
    GroupCreate(slug="technicien_reseau", name="Technicien réseau", description="Visibilité limitée aux techniciens réseau."),
]


async def ensure_default_groups(db: AsyncSession) -> None:
    for grp in DEFAULT_GROUPS:
        existing = await crud_groups.get_group_by_slug(grp.slug, db)
        if existing:
            continue
        try:
            await crud_groups.create_group(grp, db)
        except Exception:
            # Best-effort: ne pas bloquer le démarrage si un groupe existe déjà
            # (ex: conflit sur le nom unique avec un slug différent).
            continue
