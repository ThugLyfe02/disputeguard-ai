from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)

    merchant_id = Column(Integer)

    email = Column(String)
    device_fingerprint = Column(String)
    ip_address = Column(String)
