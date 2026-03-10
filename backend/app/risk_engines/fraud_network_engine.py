"""
fraud_network_engine.py

Fraud Network Risk Engine

Evaluates fraud risk using the global fraud intelligence graph.

Signals extracted:

• cluster_size
• device_reuse_signal
• cross_merchant_signal
• dispute_ratio
• velocity_signal (temporal graph)
• propagated_risk (multi-hop influence)

These signals are combined into a normalized risk score that feeds into
the RiskOrchestrator.
"""

from app.risk_engines.base_engine import RiskEngine

from app.services.fraud_network_graph import fraud_graph
from app.services.temporal_graph import temporal_graph
from app.services.graph_signal_cache import graph_signal_cache


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
        device_node = f"device_{device_hash}"
        merchant_node = f"merchant_{merchant_id}"

        # --------------------------------------------------
        # Retrieve Cached Graph Signals
        # --------------------------------------------------

        cluster_risk = graph_signal_cache.get_cluster_risk(tx_node)
        device_reuse = graph_signal_cache.get_device_reuse(device_node)
        cross_merchant = graph_signal_cache.get_cross_merchant(tx_node)
        velocity_signal = graph_signal_cache.get_velocity(tx_node)
        cluster_size = graph_signal_cache.get_cluster_size(tx_node)

        # --------------------------------------------------
        # Fallback: Compute signals if cache empty
        # --------------------------------------------------

        if cluster_size == 0:

            cluster_result = fraud_graph.detect_cluster(tx_node)
            cluster = cluster_result["nodes"]

            if not cluster:
                return {
                    "score": 0.0,
                    "details": {"reason": "no_cluster"}
                }

            cluster_size = len(cluster)
            cluster_risk = fraud_graph.calculate_network_risk(cluster)

        else:

            cluster_result = fraud_graph.detect_cluster(tx_node)
            cluster = cluster_result["nodes"]

        # --------------------------------------------------
        # Risk Propagation
        # --------------------------------------------------

        propagation_map = fraud_graph.propagate_risk(tx_node)

        if propagation_map:
            propagated_risk = max(
                (1 / (depth + 1)) for depth in propagation_map.values()
            )
        else:
            propagated_risk = 0

        # --------------------------------------------------
        # Composite Risk Model
        # --------------------------------------------------

        score = (
            0.35 * cluster_risk +
            0.20 * device_reuse +
            0.15 * cross_merchant +
            0.15 * velocity_signal +
            0.15 * propagated_risk
        )

        final_score = min(score, 1.0)

        # --------------------------------------------------
        # Return Engine Result
        # --------------------------------------------------

        return {
            "score": final_score,
            "details": {
                "cluster_size": cluster_size,
                "cluster_risk": cluster_risk,
                "device_reuse_signal": device_reuse,
                "cross_merchant_signal": cross_merchant,
                "velocity_signal": velocity_signal,
                "propagated_risk": propagated_risk,
                "cluster_entities": cluster[:20]
            }
        }