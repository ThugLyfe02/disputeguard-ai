"""
graph_signal_worker.py

Graph Signal Worker

Maintains cached graph signals asynchronously.

Purpose
-------
When the fraud graph changes, the worker recomputes signals and updates
the GraphSignalCache. This prevents the fraud pipeline from performing
expensive graph traversals.

Architecture
------------
fraud_graph update
      ↓
event_bus.publish("graph.node.updated")
      ↓
GraphSignalWorker
      ↓
graph_signal_cache.update(node)
"""

from app.services.event_bus import event_bus
from app.services.graph_signal_cache import graph_signal_cache
from app.services.fraud_network_graph import fraud_graph


class GraphSignalWorker:

    name = "graph_signal_worker"

    def handle_graph_update(self, event):

        node = event.get("node")

        if not node:
            return

        # recompute cached signals
        graph_signal_cache.update(node)

        return {
            "status": "cache_updated",
            "node": node
        }


graph_signal_worker = GraphSignalWorker()


def register_graph_signal_worker():
    """
    Register the worker with the event bus.
    """

    event_bus.subscribe(
        "graph.node.updated",
        graph_signal_worker.handle_graph_update
    )