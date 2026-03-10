import logging
import stripe
import os

from fastapi import APIRouter, Request

logger = logging.getLogger("disputeguard.stripe")

router = APIRouter(prefix="/stripe", tags=["billing"])

endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


@router.post("/webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload,
        sig_header,
        endpoint_secret
    )

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        merchant_id = session["metadata"]["merchant_id"]

        # activate subscription in your DB
        logger.info("Activate merchant: %s", merchant_id)

    return {"status": "ok"}