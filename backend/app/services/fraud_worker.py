from app.services.event_queue import pop_event
from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.fraud_alerts import generate_alert


def process_event(db):

    event = pop_event()

    if not event:
        return {"status": "empty_queue"}

    transaction = event.get("transaction")

    device_hash = event.get("device_hash")

    fraud_result = run_fraud_pipeline(
        db,
        transaction,
        device_hash
    )

    alert = generate_alert(fraud_result)

    return {
        "fraud_result": fraud_result,
        "alert": alert
    }