import os
import json
import logging

import stripe

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.services.event_processor import process_stripe_event
from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.fraud_alerts import generate_alert


router = APIRouter()
logger = logging.getLogger(__name__)


# Load Stripe secret
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")


# ================================
# Stripe Webhook Endpoint
# ================================

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stripe webhook ingestion endpoint.

    This endpoint receives all Stripe events and routes them
    through the fraud intelligence pipeline.
    """

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # ------------------------------
    # Verify webhook signature
    # ------------------------------
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            STRIPE_WEBHOOK_SECRET
        )

    except stripe.error.SignatureVerificationError:

        logger.error("Invalid Stripe webhook signature")

        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe webhook"
        )

    except Exception as e:

        logger.error(f"Webhook error: {e}")

        raise HTTPException(
            status_code=400,
            detail="Webhook processing error"
        )

    event_type = event["type"]

    logger.info(f"Stripe event received: {event_type}")


    # ------------------------------
    # Extract merchant id
    # ------------------------------
    try:

        merchant_id = (
            event["data"]["object"]
            .get("metadata", {})
            .get("merchant_id")
        )

    except Exception:

        merchant_id = None


    if not merchant_id:

        logger.warning("Webhook missing merchant_id metadata")

        return {"status": "ignored", "reason": "missing merchant_id"}


    # ------------------------------
    # Process Stripe event
    # ------------------------------

    event_result = process_stripe_event(
        db,
        event,
        merchant_id
    )


    # ------------------------------
    # Extract Stripe object
    # ------------------------------

    event_object = event["data"]["object"]


    # ------------------------------
    # Run Fraud Intelligence Pipeline
    # ------------------------------

    fraud_result = run_fraud_pipeline(
        db=db,
        transaction=event_object,
        device_hash=event_object.get("metadata", {}).get("device_hash"),
    )


    alert = generate_alert(fraud_result)


    logger.info(f"Fraud pipeline result: {fraud_result}")


    # ------------------------------
    # Structured response
    # ------------------------------

    return {
        "event_type": event_type,
        "event_result": event_result,
        "fraud_analysis": fraud_result,
        "alert": alert
    }