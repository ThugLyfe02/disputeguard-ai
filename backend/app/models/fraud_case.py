from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.models.base import Base


class FraudCase(Base):

    __tablename__ = "fraud_cases"

    id = Column(Integer, primary_key=True)

    transaction_id = Column(String)
    merchant_id = Column(String)

    risk_score = Column(Float)

    status = Column(String, default="open")
    assigned_to = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)