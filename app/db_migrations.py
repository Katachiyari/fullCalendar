from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def _sqlite_has_column(conn, table: str, column: str) -> bool:
    result = await conn.execute(text(f"PRAGMA table_info({table});"))
    rows = result.fetchall()
    return any(r[1] == column for r in rows)


async def _postgres_has_column(conn, table: str, column: str, schema: str = "public") -> bool:
    result = await conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = :schema
              AND table_name = :table
              AND column_name = :column
            LIMIT 1
            """
        ),
        {"schema": schema, "table": table, "column": column},
    )
    return result.first() is not None


async def apply_best_effort_migrations(engine: AsyncEngine) -> None:
    """Applique des migrations légères (ajout de colonnes) sans Alembic.

    Objectif: permettre d'ajouter theme/email_verified/group_id sans forcer un reset DB.
    """
    dialect = engine.url.get_backend_name()

    try:
        async with engine.begin() as conn:
            if dialect.startswith("sqlite"):
                # users
                if await _sqlite_has_column(conn, "users", "email_verified") is False:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 1"))
                if await _sqlite_has_column(conn, "users", "theme") is False:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN theme VARCHAR DEFAULT 'midnight'"))
                if await _sqlite_has_column(conn, "users", "group_id") is False:
                    await conn.execute(text("ALTER TABLE users ADD COLUMN group_id VARCHAR"))

                # events
                if await _sqlite_has_column(conn, "events", "group_id") is False:
                    await conn.execute(text("ALTER TABLE events ADD COLUMN group_id VARCHAR"))

            elif dialect.startswith("postgres"):
                # users
                if await _postgres_has_column(conn, "users", "email_verified") is False:
                    await conn.execute(text("ALTER TABLE public.users ADD COLUMN email_verified BOOLEAN DEFAULT TRUE"))
                if await _postgres_has_column(conn, "users", "theme") is False:
                    await conn.execute(text("ALTER TABLE public.users ADD COLUMN theme VARCHAR DEFAULT 'midnight'"))
                if await _postgres_has_column(conn, "users", "group_id") is False:
                    await conn.execute(text("ALTER TABLE public.users ADD COLUMN group_id VARCHAR"))

                # events
                if await _postgres_has_column(conn, "events", "group_id") is False:
                    await conn.execute(text("ALTER TABLE public.events ADD COLUMN group_id VARCHAR"))
    except Exception:
        # Best-effort: ne pas bloquer le démarrage. Les nouveaux champs
        # seront disponibles après reset DB/migration manuelle.
        return
