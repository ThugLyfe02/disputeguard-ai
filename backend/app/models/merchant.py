from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    api_key = Column(String)
