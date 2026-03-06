from sqlalchemy import Column, Integer, String
from app.models.base import Base


class FraudSignal(Base):
    __tablename__ = "fraud_signals"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String)
    signal_type = Column(String)
    description = Column(String)
