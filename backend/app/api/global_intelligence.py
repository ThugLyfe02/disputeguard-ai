from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.intelligence_aggregator import get_global_risk

router = APIRouter()


@router.get("/fraud/global/{entity_type}/{entity_id}")
def global_risk(entity_type: str, entity_id: str, db: Session = Depends(get_db)):

    return get_global_risk(db, entity_type, entity_id)