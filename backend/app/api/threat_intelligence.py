from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.threat_feed_ingestion import ingest_indicator
from app.services.threat_intelligence import lookup_threat_indicator

router = APIRouter()


@router.post("/fraud/threat/intel")
def add_indicator(data: dict, db: Session = Depends(get_db)):

    return ingest_indicator(
        db,
        data["indicator_type"],
        data["indicator_value"],
        data["threat_level"],
        data.get("source", "manual")
    )


@router.get("/fraud/threat/{indicator_type}/{indicator_value}")
def get_indicator(indicator_type: str, indicator_value: str, db: Session = Depends(get_db)):

    return lookup_threat_indicator(db, indicator_type, indicator_value)