from sqlalchemy import Column, Integer, String, Text
from app.models.base import Base


class DisputeResponse(Base):
    __tablename__ = "dispute_responses"

    id = Column(Integer, primary_key=True)
    dispute_id = Column(String)
    response_text = Column(Text)
