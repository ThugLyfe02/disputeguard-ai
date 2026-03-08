"""
Fraud Network Builder

Maintains a continuously evolving fraud intelligence graph.

The graph links:

• transactions
• devices
• customers
• emails
• merchants

This allows the system to detect:

• fraud rings
• device sharing across merchants
• coordinated attacks
• mule networks
"""

from collections import defaultdict


# Global in-memory fraud graph
# In production this would be Neo4j / TigerGraph / RedisGraph

_fraud_network = defaultdict(set)


# ---------------------------------------------------------
# Node Linking
# ---------------------------------------------------------

def link_entities(entity_a: str, entity_b: str):
    """
    Link two entities in the fraud network.
    """

    _fraud_network[entity_a].add(entity_b)
    _fraud_network[entity_b].add(entity_a)


# ---------------------------------------------------------
# Event-Based Graph Updates
# ---------------------------------------------------------

def update_network_from_transaction(transaction: dict, device_hash: str):
    """
    Expand the fraud network using a new transaction.
    """

    tx_id = f"tx_{transaction.get('id')}"
    merchant_id = f"merchant_{transaction.get('merchant_id')}"
    customer_id = f"customer_{transaction.get('customer_id')}"
    email = f"email_{transaction.get('email')}"
    device = f"device_{device_hash}"

    entities = [
        tx_id,
        merchant_id,
        customer_id,
        email,
        device
    ]

    for entity in entities:
        for other in entities:

            if entity != other:
                link_entities(entity, other)

    return {
        "transaction": tx_id,
        "entities_linked": len(entities)
    }


# ---------------------------------------------------------
# Cluster Detection
# ---------------------------------------------------------

def get_entity_cluster(entity: str):
    """
    Return all connected nodes in the fraud graph.
    """

    visited = set()
    stack = [entity]

    while stack:

        node = stack.pop()

        if node not in visited:
            visited.add(node)
            stack.extend(_fraud_network.get(node, []))

    return list(visited)


# ---------------------------------------------------------
# Fraud Ring Detection
# ---------------------------------------------------------

def detect_fraud_ring(entity: str):
    """
    Identify suspicious clusters of entities.
    """

    cluster = get_entity_cluster(entity)

    device_count = sum(1 for n in cluster if n.startswith("device_"))
    merchant_count = sum(1 for n in cluster if n.startswith("merchant_"))
    tx_count = sum(1 for n in cluster if n.startswith("tx_"))

    ring_score = min((device_count + merchant_count + tx_count) / 10, 1)

    return {
        "entity": entity,
        "cluster_size": len(cluster),
        "device_count": device_count,
        "merchant_count": merchant_count,
        "transaction_count": tx_count,
        "ring_risk_score": round(ring_score, 4),
        "entities": cluster
    }


# ---------------------------------------------------------
# Global Graph Snapshot
# ---------------------------------------------------------

def export_network(limit=100):
    """
    Export a partial snapshot of the fraud network.
    """

    nodes = []
    edges = []

    count = 0

    for entity, neighbors in _fraud_network.items():

        nodes.append({
            "id": entity,
            "label": entity
        })

        for neighbor in neighbors:
            edges.append({
                "source": entity,
                "target": neighbor
            })

        count += 1

        if count > limit:
            break

    return {
        "nodes": nodes,
        "edges": edges
    }