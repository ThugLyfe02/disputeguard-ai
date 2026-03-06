from sqlalchemy import Column, Integer, String, Text
from app.models.base import Base


class EvidencePackage(Base):
    __tablename__ = "evidence_packages"

    id = Column(Integer, primary_key=True)

    merchant_id = Column(Integer)

    dispute_id = Column(String)
    evidence_summary = Column(Text)
