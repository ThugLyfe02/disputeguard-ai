from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    merchant_id = Column(Integer)

    customer_id = Column(String)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
