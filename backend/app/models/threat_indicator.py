from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class ThreatIndicator(Base):

    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True)

    indicator_type = Column(String)  # ip, email, device
    indicator_value = Column(String)

    threat_level = Column(Float)
    source = Column(String)