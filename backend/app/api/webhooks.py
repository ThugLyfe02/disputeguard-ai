from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.transaction_service import create_transaction

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):

    payload = await request.json()

    event_type = payload.get("type")

    if event_type == "payment_intent.succeeded":

        result = create_transaction(db, payload)

        return {
            "status": "transaction_recorded",
            "transaction_id": result["transaction_id"],
            "risk_score": result["risk_score"]
        }

    return {"status": "event_received"}
