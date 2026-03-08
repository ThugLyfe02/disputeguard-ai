from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_graph_analysis import analyze_entity_cluster


router = APIRouter()


@router.get("/fraud/graph/{entity}")
def visualize_fraud_graph(entity: str, db: Session = Depends(get_db)):
    """
    Returns graph cluster data for visualization.

    This endpoint allows investigators to visualize fraud
    relationships between entities such as:

    - devices
    - transactions
    - disputes
    - customers
    """

    cluster_data = analyze_entity_cluster(db, entity)

    nodes = []
    edges = []

    for node in cluster_data["cluster_entities"]:
        nodes.append({
            "id": node,
            "label": node
        })

    for node in cluster_data["cluster_entities"]:
        if node != entity:
            edges.append({
                "source": entity,
                "target": node
            })

    return {
        "entity": entity,
        "cluster_size": cluster_data["cluster_size"],
        "cluster_risk_score": cluster_data["cluster_risk_score"],
        "nodes": nodes,
        "edges": edges
    }