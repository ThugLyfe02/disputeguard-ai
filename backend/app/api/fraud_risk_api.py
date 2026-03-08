from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.security.api_key_auth import authenticate_api_key
from app.services.fraud_pipeline import run_fraud_pipeline

router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.post("/score")
def score_transaction(
    payload: dict,
    merchant=Depends(authenticate_api_key),
    db: Session = Depends(get_db),
):

    transaction = payload.get("transaction")
    device_hash = payload.get("device_hash")

    transaction["merchant_id"] = merchant["merchant_id"]

    result = run_fraud_pipeline(db, transaction, device_hash)

    return result