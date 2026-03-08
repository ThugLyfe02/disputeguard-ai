from app.services.event_queue import push_event


def ingest_event(transaction, device_hash):

    event = {
        "transaction": transaction,
        "device_hash": device_hash
    }

    return push_event(event)