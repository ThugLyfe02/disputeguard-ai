"""
fraud_network_service.py

Fraud Intelligence Network

Builds and analyzes the global fraud relationship graph
connecting:

• devices
• transactions
• customers
• disputes
• merchants

This enables detection of fraud rings and coordinated abuse.

Architecture mirrors network intelligence systems used by:

Stripe Radar
Sift
Forter
Riskified
"""

from collections import defaultdict

from app.models.transaction import Transaction
from app.models.dispute import Dispute
from app.models.device_fingerprint import DeviceFingerprint


def build_fraud_network(db):
    """
    Construct global fraud network graph.

    Nodes represent entities.
    Edges represent relationships.
    """

    graph = defaultdict(set)

    transactions = db.query(Transaction).all()
    disputes = db.query(Dispute).all()
    devices = db.query(DeviceFingerprint).all()

    # transaction ↔ merchant
    for tx in transactions:
        tx_node = f"tx_{tx.id}"
        merchant_node = f"merchant_{tx.merchant_id}"

        graph[tx_node].add(merchant_node)
        graph[merchant_node].add(tx_node)

    # device ↔ transaction
    for device in devices:
        device_node = f"device_{device.device_hash}"
        tx_node = f"tx_{device.transaction_id}"

        graph[device_node].add(tx_node)
        graph[tx_node].add(device_node)

    # disputes ↔ transaction
    for dispute in disputes:
        dispute_node = f"dispute_{dispute.id}"
        tx_node = f"tx_{dispute.transaction_id}"

        graph[dispute_node].add(tx_node)
        graph[tx_node].add(dispute_node)

    return graph


def analyze_network_cluster(graph, entity):
    """
    Find connected fraud cluster.
    """

    visited = set()
    stack = [entity]

    while stack:
        node = stack.pop()

        if node not in visited:
            visited.add(node)

            for neighbor in graph.get(node, []):
                stack.append(neighbor)

    return list(visited)


def calculate_network_risk(db, entity):
    """
    Compute network fraud risk score.
    """

    graph = build_fraud_network(db)

    cluster = analyze_network_cluster(graph, entity)

    dispute_nodes = [n for n in cluster if n.startswith("dispute_")]
    tx_nodes = [n for n in cluster if n.startswith("tx_")]

    if not tx_nodes:
        return 0

    dispute_ratio = len(dispute_nodes) / len(tx_nodes)

    return min(dispute_ratio * 2, 1)