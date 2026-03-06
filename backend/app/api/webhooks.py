from fastapi import APIRouter, Request, HTTPException
import stripe

from app.services.fraud_signals import calculate_risk_score

router = APIRouter()

# In production this should come from environment variables
STRIPE_WEBHOOK_SECRET = "whsec_test_key"


@router.post("/stripe")
async def stripe_webhook(request: Request):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    event_type = event["type"]

    # Handle payment success
    if event_type == "payment_intent.succeeded":
        transaction = event["data"]["object"]

        risk_score = calculate_risk_score(transaction)

        print("Payment succeeded:", transaction["id"])
        print("Risk score:", risk_score)

        return {"status": "payment_processed", "risk_score": risk_score}

    # Handle disputes (chargebacks)
    elif event_type == "charge.dispute.created":
        dispute = event["data"]["object"]

        print("Dispute created:", dispute["id"])

        return {"status": "dispute_received"}

    else:
        print("Unhandled event:", event_type)

    return {"status": "event_received"}
