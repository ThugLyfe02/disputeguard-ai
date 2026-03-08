"""
fraud_risk_api.py

Fraud scoring API endpoint.

Allows merchants to submit transactions to DisputeGuard AI
for fraud analysis.

Security:
• API key authentication
• Merchant isolation
• Idempotent scoring
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.api_key_auth import authenticate_api_key
from app.services.fraud_pipeline import run_fraud_pipeline

router = APIRouter(
    prefix="/fraud",
    tags=["fraud"]
)


@router.post("/score")
def score_transaction(
    payload: dict,
    merchant=Depends(authenticate_api_key),
    db: Session = Depends(get_db),
):
    """
    Score a transaction using the DisputeGuard AI fraud pipeline.
    """

    # -----------------------------------------
    # Validate payload
    # -----------------------------------------

    transaction = payload.get("transaction")
    device_hash = payload.get("device_hash")

    if not transaction:
        raise HTTPException(
            status_code=400,
            detail="Missing transaction payload"
        )

    if not device_hash:
        raise HTTPException(
            status_code=400,
            detail="Missing device_hash"
        )

    # -----------------------------------------
    # Attach merchant context
    # -----------------------------------------

    transaction["merchant_id"] = merchant["merchant_id"]

    # -----------------------------------------
    # Run fraud pipeline
    # -----------------------------------------

    try:

        result = run_fraud_pipeline(
            db=db,
            transaction=transaction,
            device_hash=device_hash
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Fraud scoring failed: {str(e)}"
        )