from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_graph_analysis import analyze_entity_cluster

router = APIRouter()


@router.get("/fraud/rings/{entity}")
def get_fraud_ring(entity: str, db: Session = Depends(get_db)):

    analysis = analyze_entity_cluster(db, entity)

    return analysis
