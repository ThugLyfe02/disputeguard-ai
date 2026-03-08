"""
graph_signal_cache.py

Stripe-style Graph Signal Cache

Maintains precomputed fraud signals derived from the fraud network graph.

Purpose
-------
Graph traversal is expensive. Instead of computing signals repeatedly
inside risk engines, this module caches high-value graph features so that
risk engines can retrieve them in O(1) time.

Signals Cached
--------------

device_reuse_score
cross_merchant_score
cluster_risk_score
velocity_score
cluster_size

Architecture
------------

fraud_graph update
        ↓
graph_signal_cache.update(node)
        ↓
cached signals available to engines
"""

from collections import defaultdict
from typing import Dict

from app.services.fraud_network_graph import fraud_graph
from app.services.temporal_graph import temporal_graph


class GraphSignalCache:

    def __init__(self):

        self.device_reuse: Dict[str, float] = defaultdict(float)
        self.cross_merchant: Dict[str, float] = defaultdict(float)
        self.cluster_risk: Dict[str, float] = defaultdict(float)
        self.velocity_score: Dict[str, float] = defaultdict(float)
        self.cluster_size: Dict[str, int] = defaultdict(int)

    # --------------------------------------------------
    # Update Signals
    # --------------------------------------------------

    def update(self, node: str):
        """
        Update cached signals for a node after graph expansion.
        """

        cluster = fraud_graph.detect_cluster(node)

        if not cluster:
            return

        risk = fraud_graph.calculate_network_risk(cluster)

        devices = [n for n in cluster if n.startswith("device_")]
        merchants = [n for n in cluster if n.startswith("merchant_")]

        cluster_size = len(cluster)

        # device reuse
        for device in devices:
            reuse_score = min(len(merchants) / 5, 1.0)
            self.device_reuse[device] = reuse_score

        # cross merchant spread
        cross_score = min(len(merchants) / 10, 1.0)

        for node in cluster:
            self.cross_merchant[node] = cross_score

        # cluster risk
        for node in cluster:
            self.cluster_risk[node] = risk

        # velocity signal
        for node in cluster:
            velocity = temporal_graph.connection_velocity(node)
            self.velocity_score[node] = min(velocity / 10, 1.0)

        # cluster size
        for node in cluster:
            self.cluster_size[node] = cluster_size

    # --------------------------------------------------
    # Accessors
    # --------------------------------------------------

    def get_device_reuse(self, device_node):
        return self.device_reuse.get(device_node, 0)

    def get_cross_merchant(self, node):
        return self.cross_merchant.get(node, 0)

    def get_cluster_risk(self, node):
        return self.cluster_risk.get(node, 0)

    def get_velocity(self, node):
        return self.velocity_score.get(node, 0)

    def get_cluster_size(self, node):
        return self.cluster_size.get(node, 0)


graph_signal_cache = GraphSignalCache()