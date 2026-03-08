"""
Event Stream Processor

Handles ingestion of real-time fraud events into the fraud
processing pipeline.

This is the first stage of the event-driven fraud architecture.

Responsibilities
----------------
• Normalize incoming fraud events
• Attach metadata for traceability
• Push events into the processing queue
• Enable downstream fraud workers

This architecture allows the system to support:

• Real-time fraud scoring
• Fraud graph detection
• Case management triggers
• ML training pipelines
• cross-merchant intelligence
"""

import uuid
from datetime import datetime

from app.services.event_queue import push_event


def ingest_event(transaction: dict, device_hash: str, merchant_id: str):
    """
    Ingest a fraud event into the event queue.

    Parameters
    ----------
    transaction : dict
        Raw transaction payload

    device_hash : str
        Device fingerprint hash

    merchant_id : str
        Merchant identifier

    Returns
    -------
    dict
        Event metadata
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

    push_event(event)

    return {
        "status": "event_queued",
        "event_id": event_id
    }