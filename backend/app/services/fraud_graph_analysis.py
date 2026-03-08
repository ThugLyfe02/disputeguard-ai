from app.services.fraud_graph_builder import build_fraud_graph
from app.services.fraud_ring_score import score_fraud_cluster


def analyze_entity_cluster(db, entity):

    graph = build_fraud_graph(db)

    cluster = graph.detect_cluster(entity)

    risk_score = score_fraud_cluster(db, cluster)

    return {
        "entity": entity,
        "cluster_size": len(cluster),
        "cluster_entities": cluster,
        "cluster_risk_score": risk_score
    }
