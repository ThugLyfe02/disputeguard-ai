"""
fraud_network_subscriber.py

Fraud Network Subscriber
------------------------
Listens for ``"fraud.analysis.completed"`` events on the global event bus.

On each event the subscriber:

1. Rebuilds the fraud network graph via
   :func:`app.services.fraud_network_service.build_fraud_network`.
2. Runs cluster analysis on the transaction node via
   :func:`app.services.fraud_network_service.analyze_network_cluster`.

This enriches the fraud intelligence graph with new transaction data and
surfaces fraud rings that may span the newly observed transaction.
"""

import logging

from app.services.event_bus import event_bus
from app.services.fraud_network_service import build_fraud_network, analyze_network_cluster
from app.database import SessionLocal

logger = logging.getLogger("disputeguard")


def register():
    """Register the fraud network handler with the event bus."""

    def handle_event(fraud_result: dict):
        """
        Handle a ``"fraud.analysis.completed"`` event.

        Expands the fraud network graph and performs cluster analysis for the
        transaction entity found in *fraud_result*.

        Parameters
        ----------
        fraud_result : dict
            Payload published by the fraud pipeline.  Expected keys:

            * ``"transaction_id"`` (str)
        """

        transaction_id = fraud_result.get("transaction_id")
        entity = f"tx_{transaction_id}"

        logger.info(
            "[FraudNetworkSubscriber] Expanding fraud network for transaction %s.",
            transaction_id,
        )

        db = SessionLocal()
        try:
            graph = build_fraud_network(db)
            logger.info(
                "[FraudNetworkSubscriber] Fraud network built — %d nodes.",
                len(graph),
            )

            cluster = analyze_network_cluster(graph, entity)
            logger.info(
                "[FraudNetworkSubscriber] Cluster analysis for %s — %d connected nodes.",
                entity,
                len(cluster),
            )

            return {
                "status": "network_updated",
                "entity": entity,
                "cluster_size": len(cluster),
            }
        except Exception:
            logger.exception(
                "[FraudNetworkSubscriber] Failed to update fraud network for "
                "transaction %s.",
                transaction_id,
            )
            return {"status": "error", "transaction_id": transaction_id}
        finally:
            db.close()

    event_bus.subscribe("fraud.analysis.completed", handle_event)
    logger.info("[FraudNetworkSubscriber] Registered for 'fraud.analysis.completed'.")
