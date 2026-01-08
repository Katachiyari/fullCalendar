from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey, Integer, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    """Enum pour les rôles utilisateur"""
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"


class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="group")
    events = relationship("Event", back_populates="group")


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    job_title = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String)
    hashed_password = Column(String, nullable=False)  # ⭐ Nouveau
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = Column(Boolean, default=True)  # ⭐ Nouveau
    email_verified = Column(Boolean, default=True)
    theme = Column(String, default="midnight")
    group_id = Column(String, ForeignKey("groups.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="users")
    
    # Relation avec Event
    events = relationship("Event", back_populates="owner", lazy="dynamic")


class Event(Base):
    __tablename__ = "events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    start = Column(String, nullable=False)
    end = Column(String)
    color = Column(String, default="#28a745")  # green default
    resources = Column(JSON, default=list)  # ["pod-01", "server-web"]
    rrule = Column(String)  # "FREQ=WEEKLY;BYDAY=MO"
    all_day = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    group_id = Column(String, ForeignKey("groups.id"), nullable=True)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec User
    owner = relationship("User", back_populates="events")
    group = relationship("Group", back_populates="events")


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


# ------------------------------
# v2: Gestion de projets DevOps
# ------------------------------


class Priority(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class AlertStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class AlertSource(str, enum.Enum):
    PROMETHEUS = "PROMETHEUS"
    GITLAB = "GITLAB"
    ANSIBLE = "ANSIBLE"
    MANUAL = "MANUAL"


class CalendarEventType(str, enum.Enum):
    ALERT = "ALERT"
    MAINTENANCE = "MAINTENANCE"
    DEADLINE = "DEADLINE"
    VACATION = "VACATION"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False, index=True)  # ex: OPS, DEVOPS
    name = Column(String, nullable=False)
    description = Column(String)
    grafana_embed_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    sprints = relationship("Sprint", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    alerts = relationship("Alert", back_populates="project")
    calendar_entries = relationship("CalendarEntry", back_populates="project")


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")


class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    task_id = Column(String, ForeignKey("tasks.id"), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="assignees")
    user = relationship("User")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    sprint_id = Column(String, ForeignKey("sprints.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    priority = Column(SQLEnum(Priority), nullable=False, default=Priority.P3)
    estimate_hours = Column(Float)
    due_at = Column(DateTime)
    position = Column(Integer, default=0)  # ordering within a column
    gitlab_mr_url = Column(String)
    gitlab_job_url = Column(String)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    assignees = relationship("TaskAssignee", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    body = Column(String, nullable=False)
    mentions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    user = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String, ForeignKey("users.id"), index=True)
    action = Column(String, nullable=False)  # ex: task.create, task.update
    entity_type = Column(String, nullable=False)  # ex: task
    entity_id = Column(String, nullable=False)
    before = Column(JSON)
    after = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    actor = relationship("User")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    severity = Column(SQLEnum(Priority), nullable=False, default=Priority.P3)
    status = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.OPEN)
    source = Column(SQLEnum(AlertSource), nullable=False, default=AlertSource.MANUAL)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(String, ForeignKey("users.id"))

    project = relationship("Project", back_populates="alerts")


class PipelineEvent(Base):
    __tablename__ = "pipeline_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)
    source = Column(SQLEnum(AlertSource), nullable=False, default=AlertSource.GITLAB)
    status = Column(String, nullable=False)  # success/failed/running
    ref = Column(String)
    url = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class CalendarEntry(Base):
    __tablename__ = "calendar_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime)
    all_day = Column(Boolean, default=False)
    event_type = Column(SQLEnum(CalendarEventType), nullable=False, default=CalendarEventType.MAINTENANCE)
    severity = Column(SQLEnum(Priority))
    resources = Column(JSON, default=list)
    rrule = Column(String)  # recurrence rule stored server-side
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="calendar_entries")
    owner = relationship("User")


class MonitoredServer(Base):
    __tablename__ = "monitored_servers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    host = Column(String, nullable=False, index=True)
    ssh_port = Column(Integer, default=22)
    disk_path = Column(String, default="/")
    created_at = Column(DateTime, default=datetime.utcnow)
