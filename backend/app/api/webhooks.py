import stripe
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.transaction_service import create_transaction
from app.services.dispute_service import create_dispute

router = APIRouter()

# Replace later with environment variable
STRIPE_WEBHOOK_SECRET = "whsec_test_secret"


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    event_type = event["type"]

    # Handle successful payments
    if event_type == "payment_intent.succeeded":

        result = create_transaction(db, event)

        return {
            "status": "transaction_recorded",
            "transaction_id": result["transaction_id"],
            "risk_score": result["risk_score"]
        }

    # Handle chargebacks
    if event_type == "charge.dispute.created":

        result = create_dispute(db, event)

        return {
            "status": "dispute_recorded",
            "dispute_id": result["dispute_id"],
            "evidence": result["evidence"]
        }

    return {"status": "event_received"}
