from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.incident_engine import create_incident
from app.services.incident_timeline import add_event, get_timeline
from app.services.response_orchestrator import orchestrate_response

router = APIRouter()


@router.post("/fraud/soc/incident")
def create(data: dict, db: Session = Depends(get_db)):

    incident = create_incident(
        db,
        data["incident_type"],
        data["severity"],
        data["entity_id"]
    )

    return incident


@router.get("/fraud/soc/timeline/{incident_id}")
def timeline(incident_id: int, db: Session = Depends(get_db)):

    return get_timeline(db, incident_id)