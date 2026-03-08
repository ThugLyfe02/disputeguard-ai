from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base


class BehavioralSession(Base):

    __tablename__ = "behavioral_sessions"

    id = Column(Integer, primary_key=True)

    session_id = Column(String)
    merchant_id = Column(String)

    typing_speed = Column(Float)
    mouse_entropy = Column(Float)
    page_dwell_time = Column(Float)
    checkout_time = Column(Float)

    anomaly_score = Column(Float)