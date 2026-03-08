import json
import logging

logger = logging.getLogger(__name__)

def webhook(request):
    """
    Handle incoming webhooks from the payment processor.
    """
    event = json.loads(request.body)
    logger.info(f"Received event type: {event['type']}")

    # Extract metadata
    merchant_id = event["data\"["object"]["metadata"]["merchant_id"]

    # Process the event and get results
    event_result = process_stripe_event(db, event, merchant_id)

    # Extract the Stripe event object
    event_object = event["data"]["object"]

    # If the event type matches predefined types, run fraud pipeline
    if event["type"] in ("payment_intent.succeeded", "charge.dispute.created") and "transaction_id" in event_result:
        fraud_result = run_fraud_pipeline(db, event_object, "device_hash_placeholder")
        alert = generate_alert(fraud_result)

        logger.info(f"Fraud pipeline result: {fraud_result}")

        # Return detailed response for processed events
        return {
            "event_result": event_result,
            "fraud_analysis": fraud_result,
            "alert": alert
        }

    # Log and return response for unhandled events
    logger.info(f"Unhandled Stripe event type: {event['type']}")
    return {"status": "event_received", "event_result": event_result}