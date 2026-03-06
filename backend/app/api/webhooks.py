import json
import logging

logger = logging.getLogger(__name__)


def webhook(request):
    """
    Handle incoming webhooks from the payment processor.
    """
    event = json.loads(request.body)
    logger.info(f"Received event: {event['type']}")

    # Store the event object after logging the event type
    event_object = event["data"]["object"]

    merchant_id = event_object["merchant_id"]
    # Process based on the event type
    if event['type'] == 'charge.succeeded':
        # Process charge succeeded
        process_charge_succeeded(event_object)
    elif event['type'] == 'charge.failed':
        # Process charge failed
        process_charge_failed(event_object)
    else:
        logger.warning(f"Unhandled event type: {event['type']}")

    return {'status': 'success'}


def process_charge_succeeded(event_object):
    # logic for handling charge succeeded
    pass


def process_charge_failed(event_object):
    # logic for handling charge failed
    pass
