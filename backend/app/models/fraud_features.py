from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class FraudFeature(Base):

    __tablename__ = "fraud_features"

    id = Column(Integer, primary_key=True)

    transaction_id = Column(String)
    merchant_id = Column(String)

    amount = Column(Float)

    rule_score = Column(Float)
    device_risk_score = Column(Float)
    reputation_score = Column(Float)
    cluster_risk_score = Column(Float)

    chargeback_probability = Column(Float)