from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class FraudExperiment(Base):

    __tablename__ = "fraud_experiments"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    experiment_type = Column(String)  # model / policy

    variant_a = Column(String)
    variant_b = Column(String)

    traffic_split = Column(Float)  # percentage of traffic to A