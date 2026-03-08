from queue import Queue
from threading import Thread
import logging

logger = logging.getLogger(__name__)

# In-memory queue (can later swap with Redis/Kafka)
fraud_event_queue = Queue()

def publish_event(event):
    """
    Push an event into the fraud processing queue.
    """
    fraud_event_queue.put(event)
    logger.info("Fraud event queued")


def start_event_worker(processor):
    """
    Start background worker that processes fraud events.
    """

    def worker():
        while True:
            event = fraud_event_queue.get()

            try:
                processor(event)
            except Exception as e:
                logger.error(f"Fraud worker error: {e}")

            fraud_event_queue.task_done()

    thread = Thread(target=worker, daemon=True)
    thread.start()

    logger.info("Fraud worker started")