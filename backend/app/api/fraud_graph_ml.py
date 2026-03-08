from fastapi import APIRouter

from app.services.graph_ml_detector import detect_graph_fraud

router = APIRouter()


@router.get("/fraud/graph/ml/{node}")
def graph_ml(node: str):

    return detect_graph_fraud(node)