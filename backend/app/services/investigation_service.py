from sqlalchemy.orm import Session

from app.services.fraud_graph_builder import build_fraud_graph
from app.services.fraud_graph_analysis import analyze_entity_cluster
from app.services.reputation_service import get_reputation


def investigate_entity(db: Session, entity: str):
    """
    Investigate an entity using the fraud graph.

    Returns:
    - cluster members
    - cluster risk
    - entity reputation
    """

    graph = build_fraud_graph(db)

    cluster = graph.detect_cluster(entity)

    analysis = analyze_entity_cluster(db, entity)

    reputation = get_reputation(
        db,
        entity_type="device",
        entity_id=entity
    )

    return {
        "entity": entity,
        "cluster_size": len(cluster),
        "cluster_entities": cluster,
        "cluster_risk_score": analysis.get("cluster_risk_score"),
        "reputation_score": reputation.get("reputation_score"),
        "risk_level": analysis.get("risk_level")
    }