from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class GlobalFraudSignal(Base):

    __tablename__ = "global_fraud_signals"

    id = Column(Integer, primary_key=True)

    entity_type = Column(String)  # device, email, ip
    entity_id = Column(String)

    merchant_count = Column(Integer)
    dispute_count = Column(Integer)

    global_risk_score = Column(Float)