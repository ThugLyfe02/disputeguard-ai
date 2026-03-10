"""
fraud_graph_builder.py

Builds a FraudGraph from stored transactions and disputes.

Used by fraud_graph_analysis.py and investigation_service.py to create
a session-scoped graph for entity cluster analysis.
"""

from app.services.fraud_graph import FraudGraph
from app.models.transaction import Transaction
from app.models.dispute import Dispute


def build_fraud_graph(db):
    """
    Build a FraudGraph from all transactions and disputes in the database.

    Returns a FraudGraph instance with edges between:
    - tx_<id> ↔ merchant_<merchant_id>
    - tx_<id> ↔ device_<device_hash> (if available)
    - tx_<id> ↔ dispute_<dispute_id> (if disputed)
    """

    graph = FraudGraph()

    transactions = db.query(Transaction).all()

    for tx in transactions:
        tx_node = f"tx_{tx.id}"
        merchant_node = f"merchant_{tx.merchant_id}"

        graph.add_relation(tx_node, merchant_node)

        if hasattr(tx, "device_hash") and tx.device_hash:
            graph.add_relation(tx_node, f"device_{tx.device_hash}")

    disputes = db.query(Dispute).all()

    for dispute in disputes:
        graph.add_relation(
            f"tx_{dispute.transaction_id}",
            f"dispute_{dispute.id}",
        )

    return graph
