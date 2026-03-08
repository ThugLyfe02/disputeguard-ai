from app.services.fraud_graph_builder import build_fraud_graph


def build_visual_graph(db):

    graph = build_fraud_graph(db)

    nodes = []
    edges = []

    visited = set()

    for entity, connections in graph.graph.items():

        if entity not in visited:

            nodes.append({
                "id": entity,
                "label": entity,
                "type": entity.split("_")[0]
            })

            visited.add(entity)

        for connected in connections:

            edges.append({
                "source": entity,
                "target": connected
            })

    return {
        "nodes": nodes,
        "edges": edges
    }