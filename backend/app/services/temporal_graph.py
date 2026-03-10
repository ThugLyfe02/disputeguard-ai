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

    def velocity_signal(self, node: str, cap: int = 20):
        """
        Normalize velocity into a risk signal.
        """

        velocity = self.connection_velocity(node)

        return min(velocity / cap, 1.0)

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