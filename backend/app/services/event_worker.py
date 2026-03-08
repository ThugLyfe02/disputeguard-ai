import logging

from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.fraud_alerts import generate_alert
from app.services.event_processor import process_stripe_event

logger = logging.getLogger(__name__)

def process_event(event_payload):
    """
    Main fraud event worker.
    """

    merchant_id = event_payload["merchant_id"]
    event = event_payload["event"]

    logger.info("Processing streamed fraud event")

    event_result = process_stripe_event(None, event, merchant_id)

    event_object = event["data"]["object"]

    fraud_result = run_fraud_pipeline(
        None,
        event_object,
        event_object.get("device_hash", "unknown")
    )

    alert = generate_alert(fraud_result)

    return {
        "event_result": event_result,
        "fraud_analysis": fraud_result,
        "alert": alert
    }