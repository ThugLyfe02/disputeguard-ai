from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime

from app.models.base import Base


class FraudCase(Base):
    """
    Fraud investigation case.

    Created when a transaction crosses
    risk thresholds or triggers alerts.
    """

    __tablename__ = "fraud_cases"

    id = Column(Integer, primary_key=True)

    transaction_id = Column(String)
    merchant_id = Column(String)

    risk_score = Column(Float)

    case_status = Column(String, default="open")
    case_priority = Column(String, default="medium")

    alert_type = Column(String)

    investigation_notes = Column(String)

    fraud_analysis = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)