from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.investigation_service import investigate_entity

router = APIRouter()


@router.get("/fraud/investigate/{entity}")
def investigate(entity: str, db: Session = Depends(get_db)):
    """
    Perform a fraud investigation on a given entity.

    Entities can include:
    - device hash
    - transaction id
    - email
    - IP address

    The investigation engine analyzes:
    - fraud graph cluster connections
    - cross-merchant activity
    - reputation scoring
    - fraud ring detection
    """

    report = investigate_entity(db, entity)

    return {
        "status": "investigation_complete",
        "report": report
    }