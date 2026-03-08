from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class FraudExperimentResult(Base):

    __tablename__ = "fraud_experiment_results"

    id = Column(Integer, primary_key=True)

    experiment_id = Column(Integer)

    variant = Column(String)

    fraud_detected = Column(Integer)
    false_positives = Column(Integer)
    transactions = Column(Integer)