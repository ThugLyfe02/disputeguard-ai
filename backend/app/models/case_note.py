from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base


class CaseNote(Base):

    __tablename__ = "fraud_case_notes"

    id = Column(Integer, primary_key=True)

    case_id = Column(Integer)

    analyst = Column(String)

    note = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)