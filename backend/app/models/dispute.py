from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String)
    reason = Column(String)
    amount = Column(Float)
    status = Column(String)
