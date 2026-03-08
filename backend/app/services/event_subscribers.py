from app.services.event_bus import event_bus
from app.services.fraud_pipeline import run_fraud_pipeline


def fraud_pipeline_handler(payload):
    db = payload["db"]
    transaction = payload["transaction"]
    device_hash = payload["device_hash"]

    return run_fraud_pipeline(db, transaction, device_hash)


event_bus.subscribe(
    "transaction_event",
    fraud_pipeline_handler
)