from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    merchant_id = Column(String)
    customer_id = Column(String)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
