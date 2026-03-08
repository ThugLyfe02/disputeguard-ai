"""
graph_feature_engine.py

Graph Feature Extraction Engine

Transforms fraud graph intelligence into structured features used by:

• ML training
• analytics dashboards
• fraud case investigation
• feature store persistence

This is the final layer before the feature store.
"""

from app.services.fraud_network_graph import fraud_graph
from app.services.temporal_graph import temporal_graph
from app.services.graph_signal_cache import graph_signal_cache


class GraphFeatureEngine:

    name = "graph_feature_engine"

    def extract(self, transaction_id: str, device_hash: str, merchant_id: str):

        tx_node = f"tx_{transaction_id}"
        device_node = f"device_{device_hash}"
        merchant_node = f"merchant_{merchant_id}"

        # Cached graph signals
        cluster_risk = graph_signal_cache.get_cluster_risk(tx_node)
        device_reuse = graph_signal_cache.get_device_reuse(device_node)
        merchant_spread = graph_signal_cache.get_cross_merchant(tx_node)
        velocity = graph_signal_cache.get_velocity(tx_node)
        cluster_size = graph_signal_cache.get_cluster_size(tx_node)

        # Multi-hop neighbors
        multi_hop_neighbors = fraud_graph.multi_hop_neighbors(tx_node, depth=2)

        # Temporal signals
        burst_info = temporal_graph.detect_burst(tx_node)

        return {

            "cluster_size": cluster_size,

            "device_reuse_score": device_reuse,

            "merchant_spread_score": merchant_spread,

            "velocity_score": velocity,

            "cluster_risk_score": cluster_risk,

            "multi_hop_neighbor_count": len(multi_hop_neighbors),

            "burst_activity_detected": burst_info.get("burst_detected", False),

        }


graph_feature_engine = GraphFeatureEngine()