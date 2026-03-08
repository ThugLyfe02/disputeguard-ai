from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base


class FraudAttackEvent(Base):

    __tablename__ = "fraud_attack_events"

    id = Column(Integer, primary_key=True)

    attack_type = Column(String)

    entity_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)