from sqlalchemy import Column, Integer, String
from app.models.base import Base


class DeviceFingerprint(Base):
    __tablename__ = "device_fingerprints"

    id = Column(Integer, primary_key=True)

    merchant_id = Column(Integer)

    customer_id = Column(String)

    device_hash = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    os = Column(String)
    browser = Column(String)
