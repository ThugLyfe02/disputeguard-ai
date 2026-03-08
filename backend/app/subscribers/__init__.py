"""
subscribers

Event-driven subscriber modules for the DisputeGuard AI fraud intelligence
platform.

Each subscriber registers a handler with the global event bus and reacts
to specific fraud pipeline events.

Subscribers
-----------
case_management_subscriber
    Opens fraud investigation cases when high-risk activity is detected.

fraud_network_subscriber
    Expands the fraud intelligence network graph.

feature_store_subscriber
    Captures fraud signals for ML training datasets.

graph_signal_worker
    Maintains the Graph Signal Cache asynchronously.
"""

from app.subscribers import (
    case_management_subscriber,
    fraud_network_subscriber,
    feature_store_subscriber,
)

from app.services.graph_signal_worker import register_graph_signal_worker


def register_all_subscribers():
    """
    Register all event-driven subscribers.

    Called during FastAPI startup to wire the event bus to all
    fraud intelligence modules.
    """

    case_management_subscriber.register()
    fraud_network_subscriber.register()
    feature_store_subscriber.register()

    # Graph signal cache worker
    register_graph_signal_worker()