import json
import logging
import stripe

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.event_stream import publish_event
from app.services.event_processor import process_stripe_event
from app.logger import logger

router = APIRouter()

# Stripe webhook secret from environment (recommended)
import os
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle incoming Stripe webhook events.

    This endpoint performs minimal synchronous work:
    1. Validate Stripe signature
    2. Extract merchant_id
    3. Publish event to fraud event stream

    The heavy fraud processing happens asynchronously
    via the event worker pipeline.
    """

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
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except Exception as e:
        logger.error(f"Webhook parsing error: {e}")
        raise HTTPException(status_code=400, detail="Webhook parsing failed")

    event_type = event["type"]

    logger.info(f"Stripe event received: {event_type}")

    # Extract Stripe object
    event_object = event["data"]["object"]

    # Safely extract merchant_id from metadata
    merchant_id = (
        event_object.get("metadata", {}).get("merchant_id")
    )

    if not merchant_id:
        logger.warning("Missing merchant_id in Stripe metadata")
        merchant_id = "unknown"

    # Push event into streaming fraud pipeline
    publish_event({
        "merchant_id": merchant_id,
        "event": event
    })

    logger.info(
        f"Event queued for fraud analysis: type={event_type}, merchant={merchant_id}"
    )

    return {
        "status": "event_queued",
        "event_type": event_type,
        "merchant_id": merchant_id
    }