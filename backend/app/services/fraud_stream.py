import asyncio
from collections import deque
from datetime import datetime


class FraudEventStream:
    """
    In-memory fraud intelligence stream.

    This acts as a lightweight event bus that publishes
    fraud intelligence events to connected listeners.
    """

    def __init__(self, max_events: int = 500):
        self.events = deque(maxlen=max_events)
        self.listeners = []

    def publish(self, event_type: str, payload: dict):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "payload": payload
        }

        self.events.append(event)

        for listener in self.listeners:
            listener.put_nowait(event)

    async def subscribe(self):
        queue = asyncio.Queue()
        self.listeners.append(queue)

        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self.listeners.remove(queue)


fraud_stream = FraudEventStream()