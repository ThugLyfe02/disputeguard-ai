"""
Event Stream Processor

Handles ingestion and processing of real-time fraud events.

Architecture goals:
• event-driven fraud detection
• asynchronous processing
• scalable queue ingestion
• fraud intelligence propagation

This module powers:
• real-time fraud scoring
• fraud worker processing
• graph expansion
• alert pipelines
"""

import uuid
from datetime import datetime

from app.services.event_queue import push_event, pop_event, queue_size
from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.fraud_network_builder import update_network_from_transaction


# ---------------------------------------------------
# Event Ingestion
# ---------------------------------------------------

def ingest_event(transaction: dict, device_hash: str, merchant_id: str):
    """
    Ingest a fraud event into the event queue.

    This is the entry point for:

    • webhooks
    • API ingestion
    • fraud monitoring systems
    """

    event_id = str(uuid.uuid4())

    event = {
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "transaction_fraud_check",
        "merchant_id": merchant_id,
        "payload": {
            "transaction": transaction,
            "device_hash": device_hash
        },
        "metadata": {
            "source": "fraud_api",
            "version": "v1"
        }
    }

    # Expand fraud intelligence network
    update_network_from_transaction(transaction, device_hash)

    push_event(event)

    return {
        "status": "event_queued",
        "event_id": event_id,
        "queue_size": queue_size()
    }


# ---------------------------------------------------
# Worker Processing
# ---------------------------------------------------

def process_next_event(db):
    """
    Fraud worker loop.

    Processes events from the fraud queue.
    """

    event = pop_event()

    if event is None:
        return {"status": "queue_empty"}

    payload = event["payload"]

    transaction = payload["transaction"]
    device_hash = payload["device_hash"]

    result = run_fraud_pipeline(
        db=db,
        transaction=transaction,
        device_hash=device_hash
    )

    return {
        "status": "processed",
        "event_id": event["event_id"],
        "fraud_result": result
    }


# ---------------------------------------------------
# Queue Health
# ---------------------------------------------------

def get_queue_health():
    """
    Observability endpoint for monitoring queue health.
    """

    return {
        "queue_size": queue_size(),
        "timestamp": datetime.utcnow().isoformat()
    }