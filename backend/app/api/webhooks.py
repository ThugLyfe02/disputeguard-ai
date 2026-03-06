import os
import stripe
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.event_processor import process_stripe_event
from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.fraud_alerts import generate_alert
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

    merchant_id = event["data"]["object"]["metadata"]["merchant_id"]

    event_result = process_stripe_event(db, event, merchant_id)

    event_object = event["data"]["object"]

    if event_type in ("payment_intent.succeeded", "charge.dispute.created") and "transaction_id" in event_result:

        fraud_result = run_fraud_pipeline(
            db,
            event_object,
            "device_hash_placeholder"
        )

        alert = generate_alert(fraud_result)

        logger.info(f"Fraud pipeline result: {fraud_result}")

        return {
            "event_result": event_result,
            "fraud_analysis": fraud_result,
            "alert": alert
        }

    logger.info(f"Unhandled Stripe event type: {event_type}")

    return {"status": "event_received", "event_result": event_result}