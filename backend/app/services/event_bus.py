"""
event_bus.py

Fraud Intelligence Event Bus

This module implements an internal publish/subscribe event system used
throughout the fraud intelligence platform.

The event bus decouples fraud detection modules so that new systems
(graph intelligence, ML retraining, case management, dashboards) can
subscribe to events without modifying core pipeline logic.

Architecture Benefits
---------------------
• Event-driven fraud processing
• Decoupled fraud intelligence services
• Extensible fraud analytics ecosystem
• Replayable fraud events
• Easy migration to Kafka / Redis Streams

Typical Flow
------------
Fraud Pipeline
      ↓
fraud_event_bus.publish("fraud.analysis.completed")
      ↓
Subscribers receive event
      ↓
• Case management
• Fraud network intelligence
• Feature store updates
• ML training triggers
• Monitoring dashboards
"""

from collections import defaultdict
from datetime import datetime
import uuid
import traceback


class EventBus:
    """
    Lightweight internal event bus.

    Provides publish/subscribe capabilities for fraud intelligence modules.
    """

    def __init__(self):
        self.subscribers = defaultdict(list)
        self.event_history = []

    # --------------------------------------------------
    # Subscribe
    # --------------------------------------------------

    def subscribe(self, event_type, handler):
        """
        Register a subscriber for an event type.
        """

        self.subscribers[event_type].append(handler)

        return {
            "status": "subscribed",
            "event_type": event_type,
            "handler": handler.__name__
        }

    # --------------------------------------------------
    # Publish Event
    # --------------------------------------------------

    def publish(self, event_type, payload):
        """
        Publish an event to all registered handlers.
        """

        event_id = str(uuid.uuid4())

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

        # Store history for debugging / replay
        self.event_history.append({
            "event": event,
            "handlers_executed": len(handlers),
            "results": results
        })

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

        return {
            event: [h.__name__ for h in handlers]
            for event, handlers in self.subscribers.items()
        }

    def recent_events(self, limit=10):
        """
        Retrieve recent event history.
        """

        return self.event_history[-limit:]

    def clear_history(self):
        """
        Clear stored event history.
        """

        self.event_history.clear()

        return {"status": "history_cleared"}


# Global event bus instance
event_bus = EventBus()