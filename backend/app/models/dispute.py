from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True)

    merchant_id = Column(Integer)

    transaction_id = Column(String)
    reason = Column(String)
    amount = Column(Float)
    status = Column(String)
