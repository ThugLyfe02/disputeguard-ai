from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.transaction_service import create_transaction
from app.services.dispute_service import create_dispute

router = APIRouter()


@router.post("/simulate-dispute")
def simulate_dispute(db: Session = Depends(get_db)):

    # Fake Stripe-style transaction event
    fake_transaction = {
        "data": {
            "object": {
                "merchant_id": "test_merchant",
                "customer": "test_customer",
                "amount": 150000,
                "currency": "usd",
                "status": "succeeded"
            }
        }
    }

    transaction_result = create_transaction(db, fake_transaction)

    fake_dispute = {
        "data": {
            "object": {
                "charge": transaction_result["transaction_id"],
                "reason": "fraudulent",
                "amount": 150000,
                "status": "open"
            }
        }
    }

    dispute_result = create_dispute(db, fake_dispute)

    return {
        "transaction": transaction_result,
        "dispute": dispute_result
    }
