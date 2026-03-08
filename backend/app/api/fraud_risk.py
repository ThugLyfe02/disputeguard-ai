"""
fraud_risk.py

Public API for merchants to submit transactions
for fraud analysis.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.fraud_pipeline import run_fraud_pipeline

router = APIRouter(prefix="/fraud-risk", tags=["fraud"])


@router.post("/score")
def score_transaction(payload: dict, db: Session = Depends(get_db)):
    """
    Merchant submits a transaction for fraud scoring.
    """

    transaction = payload.get("transaction")
    device_hash = payload.get("device_hash")

    result = run_fraud_pipeline(db, transaction, device_hash)

    return result