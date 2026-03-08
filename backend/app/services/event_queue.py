"""
Fraud Event Queue

Central event buffer for the event-driven fraud intelligence architecture.

This module powers:

• Real-time fraud streaming
• Fraud worker processing
• Event replay capability
• Observability of queue health
• Event fan-out to multiple consumers

Production replacements could include:

• Kafka
• Redis Streams
• AWS SQS
• RabbitMQ
"""

from collections import deque
from threading import Lock
from datetime import datetime
from typing import Callable, Dict, List
import uuid


# ---------------------------------------------------------
# Internal Queue State
# ---------------------------------------------------------

_event_queue = deque()
_queue_lock = Lock()

# Event subscribers
_subscribers: Dict[str, List[Callable]] = {}


# ---------------------------------------------------------
# Event Publishing
# ---------------------------------------------------------

def push_event(payload: dict, event_type: str):
    """
    Add an event to the fraud queue.
    """

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "payload": payload,
        "created_at": datetime.utcnow().isoformat(),
    }

    with _queue_lock:
        _event_queue.append(event)
        size = len(_event_queue)

    return {
        "status": "queued",
        "event_id": event["event_id"],
        "queue_size": size
    }


# ---------------------------------------------------------
# Event Retrieval
# ---------------------------------------------------------

def pop_event():
    """
    Retrieve next event from the queue.
    """

    with _queue_lock:

        if len(_event_queue) == 0:
            return None

        return _event_queue.popleft()


# ---------------------------------------------------------
# Queue Metrics
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Event Subscription System
# ---------------------------------------------------------

def subscribe(event_type: str, handler: Callable):
    """
    Register a handler for a specific event type.
    """

    if event_type not in _subscribers:
        _subscribers[event_type] = []

    _subscribers[event_type].append(handler)


def process_event(event: dict):
    """
    Dispatch an event to registered subscribers.
    """

    event_type = event.get("event_type")
    handlers = _subscribers.get(event_type, [])

    results = []

    for handler in handlers:
        try:
            result = handler(event["payload"])
            results.append(result)
        except Exception as e:
            results.append({"handler_error": str(e)})

    return {
        "event_id": event.get("event_id"),
        "event_type": event_type,
        "handlers_executed": len(handlers),
        "results": results
    }


# ---------------------------------------------------------
# Worker Processing Loop
# ---------------------------------------------------------

def process_next_event():
    """
    Pop next event and process it.
    """

    event = pop_event()

    if event is None:
        return {"status": "empty"}

    return process_event(event)


def process_all_events():
    """
    Drain the queue and process all events.
    """

    processed = []

    while True:

        event = pop_event()

        if event is None:
            break

        processed.append(process_event(event))

    return {
        "processed_events": len(processed),
        "details": processed
    }