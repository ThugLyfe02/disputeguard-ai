"""
case_management_subscriber.py

Case Management Subscriber
--------------------------
Listens for ``"fraud.analysis.completed"`` events on the global event bus.

When the chargeback probability in the ML prediction exceeds 0.7 a new fraud
case is automatically created via :func:`app.services.case_management.create_case`.

This subscriber is deliberately decoupled from the fraud pipeline — it reacts
to published events rather than being called directly, which keeps the pipeline
slim and makes it easy to enable or disable case creation independently.
"""

import logging

from app.services.event_bus import event_bus
from app.services.case_management import create_case
from app.database import SessionLocal

logger = logging.getLogger("disputeguard")

CHARGEBACK_CASE_THRESHOLD = 0.7


def register():
    """Register the case management handler with the event bus."""

    def handle_event(fraud_result: dict):
        """
        Handle a ``"fraud.analysis.completed"`` event.

        A fraud case is created only when the ML-predicted chargeback
        probability exceeds :data:`CHARGEBACK_CASE_THRESHOLD`.

        Parameters
        ----------
        fraud_result : dict
            Payload published by the fraud pipeline.  Expected keys:

            * ``"transaction_id"`` (str)
            * ``"merchant_id"`` (str)
            * ``"fraud_result"`` (dict) containing ``"signals"`` → ``"ml_prediction"``
              (dict) with a ``"chargeback_probability"`` (float) sub-key.
        """

        transaction_id = fraud_result.get("transaction_id")
        merchant_id = fraud_result.get("merchant_id")
        inner = fraud_result.get("fraud_result", {})
        ml_prediction = inner.get("signals", {}).get("ml_prediction", {})
        chargeback_probability = ml_prediction.get("chargeback_probability", 0.0)

        if chargeback_probability > CHARGEBACK_CASE_THRESHOLD:
            logger.info(
                "[CaseManagementSubscriber] High chargeback probability %.4f "
                "detected for transaction %s — creating fraud case.",
                chargeback_probability,
                transaction_id,
            )

            db = SessionLocal()
            try:
                case = create_case(
                    db=db,
                    transaction_id=transaction_id,
                    merchant_id=merchant_id,
                    risk_score=chargeback_probability,
                )
                logger.info(
                    "[CaseManagementSubscriber] Fraud case created: %s",
                    getattr(case, "id", case),
                )
                return {"status": "case_created", "case": str(case)}
            except Exception:
                logger.exception(
                    "[CaseManagementSubscriber] Failed to create fraud case for "
                    "transaction %s.",
                    transaction_id,
                )
                return {"status": "error", "transaction_id": transaction_id}
            finally:
                db.close()
        else:
            logger.debug(
                "[CaseManagementSubscriber] Chargeback probability %.4f is "
                "below threshold for transaction %s — no case created.",
                chargeback_probability,
                transaction_id,
            )
            return {"status": "skipped", "reason": "below_threshold"}

    event_bus.subscribe("fraud.analysis.completed", handle_event)
    logger.info("[CaseManagementSubscriber] Registered for 'fraud.analysis.completed'.")
