from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.cross_merchant_analysis import analyze_cross_merchant_entity

router = APIRouter()


@router.get("/fraud/cross-merchant/{entity}")
def detect_cross_merchant_cluster(entity: str, db: Session = Depends(get_db)):

    result = analyze_cross_merchant_entity(db, entity)

    return result
