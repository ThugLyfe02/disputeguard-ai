"""
temporal_graph.py

Temporal Fraud Graph

Tracks the time dimension of fraud graph edges.

This allows the system to detect burst fraud activity such as:

• rapid device reuse
• merchant hopping
• bot attack waves
"""

from collections import defaultdict
from datetime import datetime


class TemporalGraph:

    def __init__(self):
        # (node_a, node_b) → timestamps
        self.edges = defaultdict(list)

    def add_edge(self, node_a: str, node_b: str):
        """
        Record a time-aware connection between two nodes.
        """

        timestamp = datetime.utcnow().timestamp()

        self.edges[(node_a, node_b)].append(timestamp)
        self.edges[(node_b, node_a)].append(timestamp)

    def recent_connections(self, node: str, window_seconds: int = 300):
        """
        Return neighbors connected within a time window.
        """

        now = datetime.utcnow().timestamp()

        neighbors = []

        for (a, b), timestamps in self.edges.items():

            if a == node:

                if any(now - t < window_seconds for t in timestamps):
                    neighbors.append(b)

        return neighbors

    def connection_velocity(self, node: str, window_seconds: int = 300):
        """
        Count recent connections for velocity scoring.
        """

        return len(self.recent_connections(node, window_seconds))


temporal_graph = TemporalGraph()