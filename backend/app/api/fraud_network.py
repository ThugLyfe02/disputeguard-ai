"""
fraud_network.py

Fraud Intelligence Network API

This endpoint exposes the global fraud relationship graph used for:

• fraud ring detection
• cross-merchant device intelligence
• coordinated fraud detection
• investigation workflows
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.services.fraud_network_service import (
    build_fraud_network,
    analyze_network_cluster,
    calculate_network_risk,
)

router = APIRouter()


@router.get("/fraud/network")
def fraud_network_overview(db: Session = Depends(get_db)):
    """
    Returns global fraud network overview.

    Useful for dashboards and visualization engines.
    """

    graph = build_fraud_network(db)

    node_count = len(graph)
    edge_count = sum(len(v) for v in graph.values())

    return {
        "nodes": node_count,
        "edges": edge_count,
        "status": "fraud network active"
    }


@router.get("/fraud/network/{entity}")
def fraud_network_entity(entity: str, db: Session = Depends(get_db)):
    """
    Investigate a specific entity in the fraud network.

    Example entities:

        device_abc123
        tx_9912
        merchant_44
        dispute_55
    """

    graph = build_fraud_network(db)

    cluster = analyze_network_cluster(graph, entity)

    risk_score = calculate_network_risk(db, entity)

    nodes = []
    edges = []

    for node in cluster:
        nodes.append({
            "id": node,
            "label": node
        })

    for node in cluster:
        for neighbor in graph.get(node, []):
            if neighbor in cluster:
                edges.append({
                    "source": node,
                    "target": neighbor
                })

    return {
        "entity": entity,
        "cluster_size": len(cluster),
        "network_risk_score": risk_score,
        "nodes": nodes,
        "edges": edges
    }


@router.get("/fraud/network/ring/{entity}")
def fraud_ring_detection(entity: str, db: Session = Depends(get_db)):
    """
    Detect potential fraud rings.

    Returns cluster members and risk level.
    """

    graph = build_fraud_network(db)

    cluster = analyze_network_cluster(graph, entity)

    risk_score = calculate_network_risk(db, entity)

    ring_detected = risk_score > 0.6 and len(cluster) > 5

    return {
        "entity": entity,
        "cluster_entities": cluster,
        "cluster_size": len(cluster),
        "network_risk_score": risk_score,
        "fraud_ring_detected": ring_detected
    }