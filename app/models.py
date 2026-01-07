from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

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
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
