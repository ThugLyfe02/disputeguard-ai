from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_graph_analysis import analyze_entity_cluster

router = APIRouter()


@router.get("/fraud/graph/{entity}")
def visualize_fraud_graph(entity: str, db: Session = Depends(get_db)):
    """
    Fraud Graph Visualization API.

    This endpoint exposes the fraud ring graph structure
    so investigators can visualize connections between:

        • devices
        • transactions
        • disputes
        • customers

    The response is formatted for graph visualization tools
    such as:

        • D3.js
        • Cytoscape
        • Sigma.js
    """

    cluster_data = analyze_entity_cluster(db, entity)

    nodes = []
    edges = []

    # Create nodes
    for node in cluster_data["cluster_entities"]:
        nodes.append({
            "id": node,
            "label": node
        })

    # Create edges
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