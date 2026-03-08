from collections import deque


# Simple in-memory queue
# Later replace with Kafka / Redis / RabbitMQ

event_queue = deque()


def push_event(event):

    event_queue.append(event)

    return {"status": "queued", "queue_size": len(event_queue)}


def pop_event():

    if event_queue:
        return event_queue.popleft()

    return None


def queue_size():

    return len(event_queue)