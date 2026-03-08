from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.reputation_service import get_reputation

router = APIRouter()


@router.get("/fraud/reputation/{entity_type}/{entity_id}")
def reputation(entity_type: str, entity_id: str, db: Session = Depends(get_db)):

    return get_reputation(db, entity_type, entity_id)