"""
graph_feature_engine.py

Graph Feature Extraction Engine

Extracts ML-ready features from the fraud network graph.

These features allow ML models to learn fraud behavior patterns
such as device reuse, fraud rings, merchant hopping, and attack bursts.

Architecture:

transaction
    ↓
fraud graph
    ↓
graph feature extraction
    ↓
ML model
"""

from app.risk_engines.base_engine import RiskEngine

from app.services.fraud_network_graph import fraud_graph
from app.services.graph_signal_cache import graph_signal_cache
from app.services.temporal_graph import temporal_graph


class GraphFeatureEngine(RiskEngine):

    name = "graph_feature_engine"

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
        # Update Graph Signal Cache
        # --------------------------------------------------

        graph_signal_cache.update(tx_node)

        # --------------------------------------------------
        # Fetch Cached Graph Signals
        # --------------------------------------------------

        signals = graph_signal_cache.get_signals(tx_node)

        device_reuse = signals["device_reuse_score"]
        cross_merchant = signals["cross_merchant_score"]
        cluster_risk = signals["cluster_risk_score"]
        velocity = signals["velocity_score"]
        cluster_size = signals["cluster_size"]
        propagated = signals["propagated_risk"]

        # --------------------------------------------------
        # Graph Structural Features
        # --------------------------------------------------

        device_degree = fraud_graph.node_degree(device_node)
        merchant_degree = fraud_graph.node_degree(merchant_node)
        tx_degree = fraud_graph.node_degree(tx_node)

        # --------------------------------------------------
        # Temporal Fraud Signals
        # --------------------------------------------------

        merchant_hopping = temporal_graph.merchant_hopping_velocity(
            device_node, window_seconds=300
        )

        # --------------------------------------------------
        # Cluster Density (from cache)
        # --------------------------------------------------

        density = signals.get("cluster_density", 0)

        # --------------------------------------------------
        # Feature Risk Score
        # --------------------------------------------------

        score = min(

            (0.20 * device_reuse) +
            (0.15 * cross_merchant) +
            (0.15 * cluster_risk) +
            (0.15 * velocity) +
            (0.10 * propagated) +
            (0.10 * min(cluster_size / 20, 1)) +
            (0.10 * min(merchant_hopping / 5, 1)) +
            (0.05 * density),

            1.0
        )

        return {

            "score": score,

            "details": {

                "device_degree": device_degree,
                "merchant_degree": merchant_degree,
                "tx_degree": tx_degree,
                "merchant_hopping": merchant_hopping,
                "cluster_density": density,

                "device_reuse_signal": device_reuse,
                "cross_merchant_signal": cross_merchant,
                "cluster_risk_signal": cluster_risk,
                "velocity_signal": velocity,
                "propagated_risk_signal": propagated,
                "cluster_size": cluster_size
            }
        }