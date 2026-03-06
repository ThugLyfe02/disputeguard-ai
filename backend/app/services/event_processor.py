from app.services.transaction_service import create_transaction
from app.services.dispute_service import create_dispute


def process_stripe_event(db, event, merchant_id):

    event_type = event.get("type")

    if event_type == "payment_intent.succeeded":
        return create_transaction(db, event, merchant_id)

    if event_type == "charge.dispute.created":
        return create_dispute(db, event, merchant_id)

    return {"status": "ignored"}
