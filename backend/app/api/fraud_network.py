"""
fraud_network.py

Fraud Intelligence Network API

Provides graph-based fraud investigation capabilities.

Features:
• fraud ring detection
• cross-merchant entity intelligence
• cluster investigation
• graph visualization for dashboards
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.services.fraud_network_graph import (
    fraud_graph,
    build_graph_from_transaction,
    detect_cluster,
    calculate_network_risk,
)

router = APIRouter()


# ---------------------------------------------------------
# NETWORK OVERVIEW
# ---------------------------------------------------------

@router.get("/fraud/network")
def fraud_network_overview(db: Session = Depends(get_db)):
    """
    Returns global fraud network overview.

    Useful for monitoring the health of the fraud intelligence
    graph and powering dashboards.  The graph is populated
    incrementally via :func:`build_graph_from_transaction` as
    transactions flow through the pipeline.
    """

    node_count = len(fraud_graph.graph)
    edge_count = sum(len(v) for v in fraud_graph.graph.values())

    if node_count == 0:
        return {
            "nodes": 0,
            "edges": 0,
            "status": "empty_network"
        }

    return {
        "nodes": node_count,
        "edges": edge_count,
        "status": "fraud_network_active"
    }


# ---------------------------------------------------------
# ENTITY INVESTIGATION
# ---------------------------------------------------------

@router.get("/fraud/network/{entity}")
def fraud_network_entity(entity: str, db: Session = Depends(get_db)):
    """
    Investigate a specific entity in the fraud network.

    Calls :func:`detect_cluster` to find all nodes reachable from
    the given entity and :func:`calculate_network_risk` to score
    the cluster.

    Example entities:
        device_abc123
        tx_9912
        merchant_44
        dispute_55
    """

    if entity not in fraud_graph.graph:
        return {
            "entity": entity,
            "cluster_size": 0,
            "network_risk_score": 0,
            "nodes": [],
            "edges": [],
            "status": "entity_not_found"
        }

    cluster = detect_cluster(entity)
    risk_score = calculate_network_risk(cluster)

    nodes = []
    edges = []

    # Build nodes
    for node in cluster:
        nodes.append({
            "id": node,
            "label": node
        })

    # Build edges
    for node in cluster:
        for neighbor in fraud_graph.get_neighbors(node):
            if neighbor in cluster:
                edges.append({
                    "source": node,
                    "target": neighbor
                })

    # Cluster density metric
    possible_edges = len(cluster) * (len(cluster) - 1)
    density = (len(edges) / possible_edges) if possible_edges else 0

    return {
        "entity": entity,
        "cluster_size": len(cluster),
        "network_risk_score": risk_score,
        "cluster_density": round(density, 4),
        "nodes": nodes,
        "edges": edges,
    }


# ---------------------------------------------------------
# FRAUD RING DETECTION
# ---------------------------------------------------------

@router.get("/fraud/network/ring/{entity}")
def fraud_ring_detection(entity: str, db: Session = Depends(get_db)):
    """
    Detect potential fraud rings.

    Calls :func:`detect_cluster` to obtain the connected component and
    :func:`calculate_network_risk` to score it.

    A fraud ring is defined as:

    • high network risk
    • cluster size threshold
    • strong connection density
    """

    if entity not in fraud_graph.graph:
        return {
            "entity": entity,
            "fraud_ring_detected": False,
            "reason": "entity_not_found"
        }

    cluster = detect_cluster(entity)
    risk_score = calculate_network_risk(cluster)

    cluster_size = len(cluster)

    nodes = []
    edges = []

    for node in cluster:
        nodes.append({
            "id": node,
            "label": node
        })

    for node in cluster:
        for neighbor in fraud_graph.get_neighbors(node):
            if neighbor in cluster:
                edges.append({
                    "source": node,
                    "target": neighbor
                })

    # Ring heuristics
    possible_edges = cluster_size * (cluster_size - 1)
    density = (len(edges) / possible_edges) if possible_edges else 0

    ring_detected = (
        risk_score > 0.6
        and cluster_size >= 3
        and density > 0.3
    )

    return {
        "entity": entity,
        "cluster_entities": cluster,
        "cluster_size": cluster_size,
        "network_risk_score": risk_score,
        "cluster_density": round(density, 4),
        "fraud_ring_detected": ring_detected
    }