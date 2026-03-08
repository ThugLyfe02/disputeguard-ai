from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base


class FraudIncident(Base):

    __tablename__ = "fraud_incidents"

    id = Column(Integer, primary_key=True)

    incident_type = Column(String)

    severity = Column(String)

    entity_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)