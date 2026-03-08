from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class Reputation(Base):
    __tablename__ = "reputation"

    id = Column(Integer, primary_key=True)

    entity_type = Column(String)     # device, email, customer, ip
    entity_id = Column(String)

    total_transactions = Column(Integer, default=0)
    total_disputes = Column(Integer, default=0)

    reputation_score = Column(Float, default=0)