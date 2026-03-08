"""
subscribers

Event-driven subscriber modules for the DisputeGuard AI fraud intelligence
platform.

Each subscriber module registers a handler with the global event bus and reacts
to ``"fraud.analysis.completed"`` events produced by the fraud pipeline.

Subscribers
-----------
* case_management_subscriber  — opens a fraud case when chargeback risk is high
* fraud_network_subscriber    — expands the fraud network intelligence graph
* feature_store_subscriber    — captures fraud signals for ML training
"""

from app.subscribers import (
    case_management_subscriber,
    fraud_network_subscriber,
    feature_store_subscriber,
)


def register_all():
    """Register all subscribers with the event bus."""

    case_management_subscriber.register()
    fraud_network_subscriber.register()
    feature_store_subscriber.register()
