from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class FraudPolicy(Base):

    __tablename__ = "fraud_policies"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    signal = Column(String)        # device_risk_score, rule_score, etc
    operator = Column(String)      # >, <, >=
    threshold = Column(Float)

    action = Column(String)        # block, review, verify