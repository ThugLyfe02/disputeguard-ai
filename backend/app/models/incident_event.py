from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base


class IncidentEvent(Base):

    __tablename__ = "incident_events"

    id = Column(Integer, primary_key=True)

    incident_id = Column(Integer)

    event_type = Column(String)

    entity_id = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)