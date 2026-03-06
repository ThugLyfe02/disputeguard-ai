import os
import stripe
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.transaction_service import create_transaction
from app.services.dispute_service import create_dispute

router = APIRouter()

# Load Stripe secret from environment
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


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

    if event_type == "payment_intent.succeeded":

        result = create_transaction(db, event)

        return {
            "status": "transaction_recorded",
            "transaction_id": result["transaction_id"],
            "risk_score": result["risk_score"]
        }

    if event_type == "charge.dispute.created":

        result = create_dispute(db, event)

        return {
            "status": "dispute_recorded",
            "dispute_id": result["dispute_id"],
            "evidence": result["evidence"]
        }

    return {"status": "event_received"}
