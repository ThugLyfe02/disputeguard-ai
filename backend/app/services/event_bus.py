"""
event_bus.py

Fraud Intelligence Event Bus

Internal publish/subscribe system used across the fraud intelligence
platform.

Architecture Benefits
---------------------
• Event-driven fraud processing
• Decoupled fraud intelligence services
• Extensible fraud analytics ecosystem
• Replayable fraud events
• Easy migration to Kafka / Redis Streams
"""

from collections import defaultdict
from datetime import datetime
from threading import RLock
import uuid
import traceback


class EventBus:
    """
    Lightweight internal event bus.

    Provides publish/subscribe capabilities for fraud intelligence modules.
    """

    MAX_HISTORY = 1000

    def __init__(self):

        # event_type -> handlers
        self.subscribers = defaultdict(list)

        # observability history
        self.event_history = []

        # idempotency protection
        self.processed_event_ids = set()

        # thread safety
        self.lock = RLock()

    # --------------------------------------------------
    # Subscribe
    # --------------------------------------------------

    def subscribe(self, event_type, handler):
        """
        Register a subscriber for an event type.
        """

        with self.lock:

            if handler not in self.subscribers[event_type]:
                self.subscribers[event_type].append(handler)

        return {
            "status": "subscribed",
            "event_type": event_type,
            "handler": handler.__name__
        }

    # --------------------------------------------------
    # Publish Event
    # --------------------------------------------------

    def publish(self, event_type, payload, event_id=None):
        """
        Publish an event to all registered handlers.

        Supports idempotency protection.
        """

        with self.lock:

            if event_id is None:
                event_id = str(uuid.uuid4())

            # ---------------------------------
            # Idempotency protection
            # ---------------------------------

            if event_id in self.processed_event_ids:
                return {
                    "status": "duplicate_event_skipped",
                    "event_id": event_id
                }

            self.processed_event_ids.add(event_id)

        event = {
            "event_id": event_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        }

        handlers = self.subscribers.get(event_type, [])

        results = []

        for handler in handlers:

            try:

                result = handler(payload)

                results.append({
                    "handler": handler.__name__,
                    "status": "success",
                    "result": result
                })

            except Exception as e:

                results.append({
                    "handler": handler.__name__,
                    "status": "error",
                    "error": str(e),
                    "trace": traceback.format_exc()
                })

        # ---------------------------------
        # Store event history (bounded)
        # ---------------------------------

        with self.lock:

            self.event_history.append({
                "event": event,
                "handlers_executed": len(handlers),
                "results": results
            })

            if len(self.event_history) > self.MAX_HISTORY:
                self.event_history.pop(0)

        return {
            "event_id": event_id,
            "handlers": len(handlers),
            "results": results
        }

    # --------------------------------------------------
    # Observability
    # --------------------------------------------------

    def list_subscribers(self):
        """
        Return all registered subscribers.
        """

        with self.lock:

            return {
                event: [h.__name__ for h in handlers]
                for event, handlers in self.subscribers.items()
            }

    def recent_events(self, limit=10):
        """
        Retrieve recent event history.
        """

        with self.lock:
            return self.event_history[-limit:]

    def clear_history(self):
        """
        Clear stored event history.
        """

        with self.lock:
            self.event_history.clear()

        return {"status": "history_cleared"}


# Global event bus instance
event_bus = EventBus()