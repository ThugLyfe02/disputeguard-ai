import os
import stripe
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.transaction_service import create_transaction
from app.services.dispute_service import create_dispute
from app.logger import logger

router = APIRouter()

# Load Stripe secret from environment
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):

    logger.info("Stripe webhook received")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid Stripe webhook signature")
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    event_type = event["type"]

    logger.info(f"Stripe event detected: {event_type}")

    if event_type == "payment_intent.succeeded":

        result = create_transaction(db, event)

        logger.info(f"Transaction stored with ID {result['transaction_id']} and risk score {result['risk_score']}")

        return {
            "status": "transaction_recorded",
            "transaction_id": result["transaction_id"],
            "risk_score": result["risk_score"]
        }

    if event_type == "charge.dispute.created":

        result = create_dispute(db, event)

        logger.info(f"Dispute recorded with ID {result['dispute_id']}")

        return {
            "status": "dispute_recorded",
            "dispute_id": result["dispute_id"],
            "evidence": result["evidence"]
        }

    logger.info(f"Unhandled Stripe event type: {event_type}")

    return {"status": "event_received"}
