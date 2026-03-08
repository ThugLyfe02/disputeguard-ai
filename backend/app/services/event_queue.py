"""
Fraud Event Queue

Central event buffer for the event-driven fraud architecture.

This module powers:

• Real-time fraud streaming
• Fraud worker processing
• Event replay capability
• Observability of queue health

Production replacements could include:

• Kafka
• Redis Streams
• AWS SQS
• RabbitMQ
"""

from collections import deque
from threading import Lock
from datetime import datetime
import uuid


# ----------------------------------------------------
# In-Memory Queue
# ----------------------------------------------------

_event_queue = deque()
_queue_lock = Lock()


# ----------------------------------------------------
# Queue Operations
# ----------------------------------------------------

def push_event(payload: dict, event_type: str = "fraud_event"):
    """
    Add an event to the fraud queue.
    """

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "payload": payload,
        "created_at": datetime.utcnow().isoformat()
    }

    with _queue_lock:
        _event_queue.append(event)
        size = len(_event_queue)

    return {
        "status": "queued",
        "event_id": event["event_id"],
        "queue_size": size
    }


def pop_event():
    """
    Retrieve next event from the queue.
    """

    with _queue_lock:

        if len(_event_queue) == 0:
            return None

        return _event_queue.popleft()


def queue_size():
    """
    Return current queue size.
    """

    with _queue_lock:
        return len(_event_queue)


def peek_events(limit: int = 10):
    """
    Inspect events without removing them.
    Useful for debugging or dashboards.
    """

    with _queue_lock:
        return list(_event_queue)[:limit]


def clear_queue():
    """
    Clear the queue (useful for tests).
    """

    with _queue_lock:
        _event_queue.clear()

    return {"status": "cleared"}