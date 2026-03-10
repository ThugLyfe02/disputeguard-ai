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
propagated_risk

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
import logging
import threading
import time

from app.services.fraud_network_graph import fraud_graph
from app.services.temporal_graph import temporal_graph

logger = logging.getLogger("disputeguard.graph_signal_cache")


class GraphSignalCache:

    # cache refresh TTL (seconds)
    CACHE_TTL = 30

    # Refresh-ahead threshold: trigger background refresh when this
    # fraction of the TTL has elapsed (0.8 = 80%).
    REFRESH_AHEAD_RATIO = 0.80

    # Maximum cached entries — prevents unbounded memory growth
    MAX_CACHE_ENTRIES = 100_000

    # Stale entry eviction age (seconds)
    STALE_AGE = 300

    def __init__(self):

        # graph signals
        self.device_reuse: Dict[str, float] = defaultdict(float)
        self.cross_merchant: Dict[str, float] = defaultdict(float)
        self.cluster_risk: Dict[str, float] = defaultdict(float)
        self.velocity_score: Dict[str, float] = defaultdict(float)
        self.cluster_size: Dict[str, int] = defaultdict(int)
        self.propagated_risk: Dict[str, float] = defaultdict(float)
        self.cluster_density: Dict[str, float] = defaultdict(float)
        self.merchant_count: Dict[str, int] = defaultdict(int)

        # refresh timestamps
        self.last_update: Dict[str, float] = defaultdict(float)

        # thread safety
        self._lock = threading.RLock()

        # Eviction counter
        self._update_count = 0

        # Track nodes with pending background refreshes to avoid spawning
        # duplicate threads for the same node.
        self._refreshing: set = set()

    # --------------------------------------------------
    # Update Signals
    # --------------------------------------------------

    def update(self, node: str):
        """
        Update cached signals for a node after graph expansion.
        """

        with self._lock:

            now = time.time()

            if now - self.last_update[node] < self.CACHE_TTL:
                return

            cluster_result = fraud_graph.detect_cluster(node)
            cluster = cluster_result["nodes"]

            if not cluster:
                return

            risk = fraud_graph.calculate_network_risk(cluster)

            devices = [n for n in cluster if n.startswith("device_")]
            merchants = [n for n in cluster if n.startswith("merchant_")]

            cluster_size = len(cluster)

            # --------------------------------------------------
            # Device reuse signal
            # --------------------------------------------------

            reuse_score = min(len(merchants) / 5, 1.0)

            for device in devices:
                self.device_reuse[device] = reuse_score

            # --------------------------------------------------
            # Cross merchant signal
            # --------------------------------------------------

            cross_score = min(len(merchants) / 10, 1.0)

            for n in cluster:
                self.cross_merchant[n] = cross_score

            # --------------------------------------------------
            # Cluster risk
            # --------------------------------------------------

            for n in cluster:
                self.cluster_risk[n] = risk

            # --------------------------------------------------
            # Temporal velocity
            # --------------------------------------------------

            for n in cluster:
                velocity = temporal_graph.connection_velocity(n)
                self.velocity_score[n] = min(velocity / 10, 1.0)

            # --------------------------------------------------
            # Risk propagation signal
            # --------------------------------------------------

            propagation = fraud_graph.propagate_risk(node)

            if propagation:
                max_prop = max(
                    (1 / (depth + 1))
                    for depth in propagation.values()
                )
            else:
                max_prop = 0

            for n in cluster:
                self.propagated_risk[n] = max_prop

            # --------------------------------------------------
            # Cluster size
            # --------------------------------------------------

            for n in cluster:
                self.cluster_size[n] = cluster_size

            # --------------------------------------------------
            # Cluster density signal
            # --------------------------------------------------

            density = fraud_graph.graph_density(cluster)

            for n in cluster:
                self.cluster_density[n] = density

            # --------------------------------------------------
            # Merchant count
            # --------------------------------------------------

            merchant_count = len(merchants)

            for n in cluster:
                self.merchant_count[n] = merchant_count

            self.last_update[node] = now

            # --------------------------------------------------
            # Periodic eviction
            # --------------------------------------------------

            self._update_count += 1
            if self._update_count % 500 == 0:
                self._evict_stale()

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

    def get_propagated_risk(self, node):
        return self.propagated_risk.get(node, 0)

    def get_cluster_density(self, node):
        return self.cluster_density.get(node, 0)

    def get_merchant_count(self, node):
        return self.merchant_count.get(node, 0)

    # --------------------------------------------------
    # Convenience aggregator
    # --------------------------------------------------

    def get_signals(self, node: str):

        # Refresh-ahead: if cache entry exists but > 80% of TTL has elapsed,
        # schedule a background refresh so the next read gets fresh data.
        self._maybe_refresh_ahead(node)

        return {

            "device_reuse_score": self.get_device_reuse(node),
            "cross_merchant_score": self.get_cross_merchant(node),
            "cluster_risk_score": self.get_cluster_risk(node),
            "velocity_score": self.get_velocity(node),
            "cluster_size": self.get_cluster_size(node),
            "propagated_risk": self.get_propagated_risk(node),
            "cluster_density": self.get_cluster_density(node),
            "merchant_count": self.get_merchant_count(node),
        }

    def _maybe_refresh_ahead(self, node: str):
        """Trigger background cache refresh when TTL is > 80% expired."""
        with self._lock:
            last = self.last_update.get(node, 0)
            if last == 0:
                return  # No cached entry — nothing to refresh ahead
            age = time.time() - last
            if age < self.CACHE_TTL * self.REFRESH_AHEAD_RATIO:
                return  # Still fresh enough
            if node in self._refreshing:
                return  # Already refreshing

            self._refreshing.add(node)

        def _background_refresh():
            try:
                self.update(node)
            except Exception:
                logger.exception("Background refresh failed for node %s", node)
            finally:
                with self._lock:
                    self._refreshing.discard(node)

        t = threading.Thread(target=_background_refresh, daemon=True)
        t.start()

    # --------------------------------------------------
    # Eviction
    # --------------------------------------------------

    def _evict_stale(self):
        """Remove cache entries older than STALE_AGE seconds."""
        now = time.time()
        stale_nodes = [
            node for node, ts in self.last_update.items()
            if now - ts > self.STALE_AGE
        ]
        for node in stale_nodes:
            self._remove_node(node)

        # Also enforce hard cap — evict oldest if over MAX_CACHE_ENTRIES
        if len(self.last_update) > self.MAX_CACHE_ENTRIES:
            sorted_nodes = sorted(self.last_update, key=self.last_update.get)
            evict_count = len(self.last_update) - self.MAX_CACHE_ENTRIES
            for node in sorted_nodes[:evict_count]:
                self._remove_node(node)

    def _remove_node(self, node: str):
        """Remove all cached signals for a single node."""
        self.device_reuse.pop(node, None)
        self.cross_merchant.pop(node, None)
        self.cluster_risk.pop(node, None)
        self.velocity_score.pop(node, None)
        self.cluster_size.pop(node, None)
        self.propagated_risk.pop(node, None)
        self.cluster_density.pop(node, None)
        self.merchant_count.pop(node, None)
        self.last_update.pop(node, None)


# Global singleton
graph_signal_cache = GraphSignalCache()