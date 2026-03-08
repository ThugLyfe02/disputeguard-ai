"""
feature_store_subscriber.py

Feature Store Subscriber
------------------------
Listens for ``"fraud.analysis.completed"`` events on the global event bus.

On each event the subscriber captures fraud signals from the pipeline result
and persists them to the feature store via
:func:`app.services.feature_store.store_features`.

Stored features are consumed by ML model training pipelines and real-time
feature retrieval to enrich future fraud predictions.
"""

import logging

from app.services.event_bus import event_bus
from app.services.feature_store import store_features
from app.database import SessionLocal

logger = logging.getLogger("disputeguard")


def register():
    """Register the feature store handler with the event bus."""

    def handle_event(fraud_result: dict):
        """
        Handle a ``"fraud.analysis.completed"`` event.

        Extracts fraud signals from *fraud_result* and persists them to the
        feature store to enrich the ML training dataset.

        Parameters
        ----------
        fraud_result : dict
            Payload published by the fraud pipeline.  Expected keys:

            * ``"transaction_id"`` (str)
            * ``"merchant_id"`` (str)
            * ``"rule_score"`` (float)
            * ``"reputation"`` (dict) with ``"reputation_score"`` (float)
            * ``"graph_cluster"`` (dict) with ``"cluster_risk_score"`` (float)
            * ``"ml_prediction"`` (dict) with:

              - ``"chargeback_probability"`` (float)
              - ``"features_used"`` (dict) with ``"amount"`` (float) and
                ``"device_risk_score"`` (float)
        """

        transaction_id = fraud_result.get("transaction_id")
        merchant_id = fraud_result.get("merchant_id")
        rule_score = fraud_result.get("rule_score", 0.0)

        ml_prediction = fraud_result.get("ml_prediction", {})
        chargeback_probability = ml_prediction.get("chargeback_probability", 0.0)
        features_used = ml_prediction.get("features_used", {})
        amount = features_used.get("amount", 0.0)
        device_risk_score = features_used.get("device_risk_score", 0.0)

        reputation = fraud_result.get("reputation", {})
        reputation_score = reputation.get("reputation_score", 0.0)

        graph_cluster = fraud_result.get("graph_cluster", {})
        cluster_risk_score = graph_cluster.get("cluster_risk_score", 0.0)

        logger.info(
            "[FeatureStoreSubscriber] Storing fraud features for transaction %s.",
            transaction_id,
        )

        db = SessionLocal()
        try:
            feature = store_features(
                db=db,
                transaction_id=transaction_id,
                merchant_id=merchant_id,
                amount=amount,
                rule_score=rule_score,
                device_risk_score=device_risk_score,
                reputation_score=reputation_score,
                cluster_risk_score=cluster_risk_score,
                chargeback_probability=chargeback_probability,
            )
            logger.info(
                "[FeatureStoreSubscriber] Features stored for transaction %s.",
                transaction_id,
            )
            return {"status": "features_stored", "transaction_id": transaction_id}
        except Exception:
            logger.exception(
                "[FeatureStoreSubscriber] Failed to store features for "
                "transaction %s.",
                transaction_id,
            )
            return {"status": "error", "transaction_id": transaction_id}
        finally:
            db.close()

    event_bus.subscribe("fraud.analysis.completed", handle_event)
    logger.info("[FeatureStoreSubscriber] Registered for 'fraud.analysis.completed'.")
