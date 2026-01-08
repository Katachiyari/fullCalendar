from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.models import User, UserRole


@dataclass(frozen=True)
class VisibilityRule:
    group_slug: str
    can_see_group_slugs: tuple[str, ...]


# Cahier des charges: matrice de visibilité minimale.
# Slugs attendus: chef_projet, developpeur, devops, technicien_reseau
_VISIBILITY: dict[str, VisibilityRule] = {
    "technicien_reseau": VisibilityRule(
        group_slug="technicien_reseau",
        can_see_group_slugs=("technicien_reseau",),
    ),
    "developpeur": VisibilityRule(
        group_slug="developpeur",
        can_see_group_slugs=("developpeur",),
    ),
    "devops": VisibilityRule(
        group_slug="devops",
        can_see_group_slugs=("devops", "developpeur", "technicien_reseau"),
    ),
    "chef_projet": VisibilityRule(
        group_slug="chef_projet",
        can_see_group_slugs=("chef_projet", "devops", "developpeur", "technicien_reseau"),
    ),
}


def get_user_group_slug(user: User) -> str | None:
    grp = getattr(user, "group", None)
    if grp is not None and getattr(grp, "slug", None):
        return grp.slug
    return None


def visible_group_slugs_for_user(user: User) -> tuple[str, ...]:
    """Retourne les slugs de groupes visibles pour l'utilisateur.

    Remarque: les ADMIN ne sont pas filtrés par groupe (géré ailleurs).
    """
    slug = get_user_group_slug(user)
    if not slug:
        return tuple()
    rule = _VISIBILITY.get(slug)
    if not rule:
        # Groupe inconnu → visibilité limitée à son groupe.
        return (slug,)
    return rule.can_see_group_slugs


def can_assign_events_to_any_group(user: User) -> bool:
    """Détermine si l'utilisateur peut choisir un groupe cible différent du sien.

    Cahier des charges:
    - Chef de projet: peut créer un RDV pour tout le monde et l'assigner à un groupe.
    - Admin: accès total.
    """
    if user.role == UserRole.ADMIN:
        return True
    return get_user_group_slug(user) == "chef_projet"


def can_manage_all_events(user: User) -> bool:
    """Chef de projet et ADMIN peuvent tout modifier/supprimer (cahier des charges)."""
    if user.role == UserRole.ADMIN:
        return True
    return get_user_group_slug(user) == "chef_projet"
