from app.services.fraud_graph_builder import build_fraud_graph
from app.services.fraud_ring_score import score_fraud_cluster


def analyze_entity_cluster(db, entity):

    # Build the relationship graph from stored transactions/disputes
    graph = build_fraud_graph(db)

    # Detect connected entities
    cluster = graph.detect_cluster(entity)

    # Score the fraud risk of that cluster
    risk_score = score_fraud_cluster(db, cluster)

    return {
        "entity": entity,
        "cluster_size": len(cluster),
        "cluster_entities": cluster,
        "cluster_risk_score": risk_score
    }