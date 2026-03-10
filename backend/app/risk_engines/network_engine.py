"""
network_engine.py

Fraud Network Risk Engine

Uses the fraud intelligence graph to detect fraud rings,
device reuse patterns, and cross-merchant connections.

Produces a normalized fraud score from graph signals.
"""

from app.risk_engines.base_engine import RiskEngine
from app.services.fraud_network_graph import fraud_graph


class NetworkEngine(RiskEngine):

    name = "network_engine"

    def evaluate(self, db, context):

        transaction = context.get("transaction")
        device_hash = context.get("device_hash")
        merchant_id = context.get("merchant_id")

        if not transaction:
            return {"score": 0.0, "details": {}}

        tx_id = f"tx_{transaction.get('id')}"

        # -------------------------------------
        # Detect cluster in fraud graph
        # -------------------------------------

        cluster_result = fraud_graph.detect_cluster(tx_id)
        cluster = cluster_result["nodes"]

        cluster_size = len(cluster)

        # -------------------------------------
        # Graph signals
        # -------------------------------------

        device_nodes = [n for n in cluster if n.startswith("device_")]
        merchant_nodes = [n for n in cluster if n.startswith("merchant_")]
        dispute_nodes = [n for n in cluster if n.startswith("dispute_")]

        device_reuse = max(len(device_nodes) - 1, 0)
        merchant_links = max(len(merchant_nodes) - 1, 0)
        dispute_ratio = len(dispute_nodes) / max(cluster_size, 1)

        # -------------------------------------
        # Risk model
        # -------------------------------------

        device_signal = min(device_reuse / 5, 1.0)
        merchant_signal = min(merchant_links / 5, 1.0)
        dispute_signal = min(dispute_ratio, 1.0)

        score = (
            0.4 * device_signal +
            0.3 * merchant_signal +
            0.3 * dispute_signal
        )

        return {
            "score": score,
            "details": {
                "cluster_size": cluster_size,
                "device_reuse": device_reuse,
                "merchant_links": merchant_links,
                "dispute_ratio": dispute_ratio,
                "cluster_entities": list(cluster)
            }
        }