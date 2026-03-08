"""
fraud_network_engine.py

Fraud Network Risk Engine

This engine evaluates fraud risk based on the global fraud network graph.

Signals extracted:

• cluster_size
• device_reuse_signal
• cross_merchant_signal
• dispute_ratio
• velocity_signal (temporal graph)
• propagated_risk

The result becomes part of the orchestrator's combined fraud score.
"""

from app.risk_engines.base_engine import RiskEngine

from app.services.fraud_network_graph import fraud_graph
from app.services.temporal_graph import temporal_graph


class FraudNetworkEngine(RiskEngine):

    name = "fraud_network_engine"

    def evaluate(self, db, context: dict):

        transaction = context.get("transaction", {})
        device_hash = context.get("device_hash")
        merchant_id = context.get("merchant_id")

        transaction_id = transaction.get("id")

        if not transaction_id:
            return {
                "score": 0.0,
                "details": {"reason": "missing_transaction_id"}
            }

        tx_node = f"tx_{transaction_id}"

        # --------------------------------------------------
        # Cluster Detection
        # --------------------------------------------------

        cluster = fraud_graph.detect_cluster(tx_node)

        if not cluster:
            return {
                "score": 0.0,
                "details": {"reason": "no_cluster"}
            }

        # --------------------------------------------------
        # Base Network Risk
        # --------------------------------------------------

        network_risk = fraud_graph.calculate_network_risk(cluster)

        # --------------------------------------------------
        # Velocity Signal
        # --------------------------------------------------

        velocity_signal = temporal_graph.velocity_signal(tx_node)

        # --------------------------------------------------
        # Risk Propagation
        # --------------------------------------------------

        propagation_map = fraud_graph.propagate_risk(tx_node)

        propagated_risk = max(
            (1 / (depth + 1)) for node, depth in propagation_map.items()
        )

        # --------------------------------------------------
        # Combine Signals
        # --------------------------------------------------

        final_score = min(
            network_risk
            + (0.15 * velocity_signal)
            + (0.1 * propagated_risk),
            1.0
        )

        return {
            "score": final_score,
            "details": {
                "cluster_size": len(cluster),
                "network_risk": network_risk,
                "velocity_signal": velocity_signal,
                "propagated_risk": propagated_risk,
                "cluster_entities": cluster[:20]
            }
        }