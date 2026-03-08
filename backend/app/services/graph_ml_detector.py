from app.services.graph_embeddings import generate_graph_embedding


def detect_graph_fraud(node):

    embedding = generate_graph_embedding(node)

    score = sum(embedding) / len(embedding)

    if score > 0.75:
        level = "high"
    elif score > 0.4:
        level = "medium"
    else:
        level = "low"

    return {
        "node": node,
        "graph_risk_score": score,
        "graph_risk_level": level
    }