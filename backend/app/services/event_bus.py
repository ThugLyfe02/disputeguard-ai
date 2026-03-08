from collections import defaultdict


class EventBus:

    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        self.subscribers[event_type].append(handler)

    def publish(self, event_type, payload):

        handlers = self.subscribers.get(event_type, [])

        results = []

        for handler in handlers:
            results.append(handler(payload))

        return results


event_bus = EventBus()