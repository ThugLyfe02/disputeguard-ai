from app.services.cross_merchant_graph import build_cross_merchant_graph
from app.services.fraud_ring_score import score_fraud_cluster


def analyze_cross_merchant_entity(db, entity):

    graph = build_cross_merchant_graph(db)

    cluster = graph.detect_cluster(entity)

    risk_score = score_fraud_cluster(db, cluster)

    merchants = [e for e in cluster if str(e).startswith("merchant_")]

    return {
        "entity": entity,
        "cluster_size": len(cluster),
        "cluster_entities": cluster,
        "cluster_merchants": merchants,
        "cluster_risk_score": risk_score
    }
