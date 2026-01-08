from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Alert, AlertSource, AlertStatus, Priority, Project, Sprint, Task, TaskStatus


async def ensure_demo_v2_data(db: AsyncSession) -> None:
    """Seed minimal demo data for v2 dashboard/kanban.

    Objectif: que Dashboard/Kanban ne soient jamais vides en environnement de démo/dev.
    Stratégie: créer un projet/sprint/tâches/alertes si manquants.
    """

    now = datetime.utcnow()

    # 1) Projet par défaut
    project_res = await db.execute(select(Project).where(Project.key == "OPS"))
    project = project_res.scalar_one_or_none()

    if project is None:
        project = Project(
            key="OPS",
            name="OpsHub",
            description="Projet par défaut (demo) pour Dashboard/Kanban.",
            created_at=now,
        )
        db.add(project)
        await db.flush()

    # 2) Sprint (au moins 1)
    sprint_res = await db.execute(select(Sprint).where(Sprint.project_id == project.id).order_by(Sprint.created_at.desc()))
    sprint = sprint_res.scalars().first()
    if sprint is None:
        sprint = Sprint(
            project_id=project.id,
            name=f"Sprint {now.strftime('%Y-%m-%d')}",
            start_date=now.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=(now + timedelta(days=14)).replace(hour=23, minute=59, second=59, microsecond=0),
            created_at=now,
        )
        db.add(sprint)
        await db.flush()

    # 3) Tâches (si aucune)
    task_count_res = await db.execute(select(func.count(Task.id)).where(Task.project_id == project.id))
    task_count = task_count_res.scalar_one() or 0
    if task_count == 0:
        tasks = [
            Task(
                project_id=project.id,
                sprint_id=sprint.id,
                title="Mettre en place le monitoring serveur",
                description="Ajouter une IP et collecter CPU/RAM/disque.",
                status=TaskStatus.TODO,
                priority=Priority.P1,
                due_at=now.replace(hour=16, minute=0, second=0, microsecond=0),
                position=1,
                created_at=now,
                updated_at=now,
            ),
            Task(
                project_id=project.id,
                sprint_id=sprint.id,
                title="Corriger drag&drop calendrier",
                description="Vérifier PUT /events/{id} et validations.",
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.P0,
                due_at=now.replace(hour=18, minute=0, second=0, microsecond=0),
                position=2,
                created_at=now,
                updated_at=now,
            ),
            Task(
                project_id=project.id,
                sprint_id=sprint.id,
                title="Durcir l'image Docker (audit)",
                description="Réduire la surface d'attaque, sécuriser les secrets, scanner les CVE.",
                status=TaskStatus.TODO,
                priority=Priority.P2,
                due_at=(now + timedelta(days=2)).replace(hour=11, minute=0, second=0, microsecond=0),
                position=3,
                created_at=now,
                updated_at=now,
            ),
        ]
        db.add_all(tasks)

    # 4) Alertes (si aucune)
    alert_count_res = await db.execute(select(func.count(Alert.id)).where(Alert.project_id == project.id))
    alert_count = alert_count_res.scalar_one() or 0
    if alert_count == 0:
        alerts = [
            Alert(
                project_id=project.id,
                title="CPU instable sur srv-ops-01",
                severity=Priority.P2,
                status=AlertStatus.OPEN,
                source=AlertSource.MANUAL,
                payload={"host": "srv-ops-01"},
                created_at=now - timedelta(minutes=12),
            ),
            Alert(
                project_id=project.id,
                title="Espace disque faible sur /data/uploads",
                severity=Priority.P1,
                status=AlertStatus.OPEN,
                source=AlertSource.MANUAL,
                payload={"path": "/data/uploads"},
                created_at=now - timedelta(hours=1, minutes=5),
            ),
        ]
        db.add_all(alerts)

    await db.commit()
