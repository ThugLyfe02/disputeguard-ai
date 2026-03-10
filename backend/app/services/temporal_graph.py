"""
temporal_graph.py

Temporal Fraud Graph

Tracks the time dimension of fraud graph edges.

This enables detection of fraud behaviors that depend on velocity:

• rapid device reuse
• merchant hopping
• bot attack bursts
• coordinated fraud rings

The temporal graph complements FraudNetworkGraph by adding
time-aware intelligence used by the FraudNetworkEngine.

Architecture
------------
Main graph: entity relationships
Temporal graph: relationship timing

Example:
    temporal_graph.add_edge("device_abc", "merchant_42")
"""

import math
from collections import defaultdict
from datetime import datetime, timedelta
import threading


class TemporalGraph:
    """
    Tracks temporal relationships between graph nodes.
    """

    def __init__(self):

        # (node_a, node_b) -> [timestamps]
        self.edges = defaultdict(list)

        # node -> set of edge keys for O(degree) lookups
        self.node_index = defaultdict(set)

        # thread safety
        self._lock = threading.RLock()

        # Auto-prune counter
        self._insert_count = 0
        self._auto_prune_ttl = 7200  # 2 hours
        self._auto_prune_interval = 1000

    # --------------------------------------------------
    # Add Temporal Edge
    # --------------------------------------------------

    def add_edge(self, node_a: str, node_b: str):
        """
        Record a time-aware connection between two nodes.
        """

        timestamp = datetime.utcnow().timestamp()

        with self._lock:

            self.edges[(node_a, node_b)].append(timestamp)
            self.edges[(node_b, node_a)].append(timestamp)

            self.node_index[node_a].add((node_a, node_b))
            self.node_index[node_b].add((node_b, node_a))

            self._insert_count += 1
            if self._insert_count % self._auto_prune_interval == 0:
                self.prune_old_edges(self._auto_prune_ttl)

    # --------------------------------------------------
    # Recent Connections
    # --------------------------------------------------

    def recent_connections(self, node: str, window_seconds: int = 120):
        """
        Return neighbors connected within a time window.
        """

        now = datetime.utcnow().timestamp()

        neighbors = []

        with self._lock:

            for key in self.node_index.get(node, set()):
                timestamps = self.edges.get(key, [])
                if any(now - t <= window_seconds for t in timestamps):
                    neighbors.append(key[1])

        return neighbors

    # --------------------------------------------------
    # Connection Velocity
    # --------------------------------------------------

    def connection_velocity(self, node: str, window_seconds: int = 120):
        """
        Count recent connections for velocity signal.
        """

        return len(self.recent_connections(node, window_seconds))

    # --------------------------------------------------
    # Burst Detection
    # --------------------------------------------------

    def detect_burst(self, node: str, threshold: int = 10, window_seconds: int = 60):
        """
        Detect suspicious bursts of connections.

        Used to identify bot attacks or card testing.
        """

        velocity = self.connection_velocity(node, window_seconds)

        return {
            "node": node,
            "velocity": velocity,
            "burst_detected": velocity >= threshold,
        }

    # --------------------------------------------------
    # Temporal Risk Signal
    # --------------------------------------------------

    def velocity_signal(self, node: str, window_seconds: int = 120, cap: int = 10):
        """
        Return normalized velocity signal in [0, 1].

        Based on recent connection count within *window_seconds*,
        divided by *cap* and clamped to 1.0.
        """

        velocity = self.connection_velocity(node, window_seconds)

        return min(velocity / cap, 1.0)

    # --------------------------------------------------
    # Merchant Hopping Velocity
    # --------------------------------------------------

    def merchant_hopping_velocity(self, device_node: str, window_seconds: int = 300):
        """
        Count distinct merchants a device connected to within a time window.

        This is a high-signal fraud indicator — legitimate devices rarely
        transact at more than 1-2 merchants within 5 minutes.
        """

        recent = self.recent_connections(device_node, window_seconds)
        merchants = {n for n in recent if n.startswith("merchant_")}
        return len(merchants)

    # --------------------------------------------------
    # Edge Decay Weight
    # --------------------------------------------------

    def edge_decay_weight(self, node_a: str, node_b: str, decay_factor: float = 3600.0):
        """
        Compute time-decay weight for the most recent edge between two nodes.

        Returns e^(-age / decay_factor) where age is seconds since the most
        recent timestamp.  Newer edges return values closer to 1.0.
        Returns 0.0 if no edge exists.
        """

        with self._lock:
            timestamps = self.edges.get((node_a, node_b), [])

        if not timestamps:
            return 0.0

        most_recent = max(timestamps)
        age = datetime.utcnow().timestamp() - most_recent
        return math.exp(-age / decay_factor)

    # --------------------------------------------------
    # Prune Old Data
    # --------------------------------------------------

    def prune_old_edges(self, ttl_seconds: int = 3600):
        """
        Remove edges older than TTL to prevent memory growth.
        """

        cutoff = datetime.utcnow() - timedelta(seconds=ttl_seconds)
        cutoff_ts = cutoff.timestamp()

        with self._lock:

            for key in list(self.edges.keys()):

                timestamps = self.edges[key]

                filtered = [t for t in timestamps if t >= cutoff_ts]

                if filtered:
                    self.edges[key] = filtered
                else:
                    del self.edges[key]
                    a, b = key
                    self.node_index[a].discard(key)
                    self.node_index[b].discard((b, a))

    # --------------------------------------------------
    # Observability
    # --------------------------------------------------

    def edge_count(self):
        """
        Return total temporal edges stored.
        """

        with self._lock:
            return len(self.edges)

    def node_activity(self, node: str):
        """
        Return activity statistics for a node.
        """

        velocity = self.connection_velocity(node)

        return {
            "node": node,
            "velocity": velocity,
            "recent_connections": self.recent_connections(node),
        }


# --------------------------------------------------
# Global Instance
# --------------------------------------------------

temporal_graph = TemporalGraph()