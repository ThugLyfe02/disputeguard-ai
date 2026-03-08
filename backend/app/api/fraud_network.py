from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_graph_visualization import build_visual_graph

router = APIRouter()


@router.get("/fraud/network")
def fraud_network(db: Session = Depends(get_db)):

    graph = build_visual_graph(db)

    return graph