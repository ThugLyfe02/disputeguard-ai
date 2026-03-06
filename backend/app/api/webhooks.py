from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.json()

    event_type = payload.get("type")

    # Log incoming event (for now)
    print(f"Received Stripe event: {event_type}")

    return {"status": "received"}
