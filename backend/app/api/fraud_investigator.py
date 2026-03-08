from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_investigator import investigate_transaction

router = APIRouter()


@router.post("/fraud/investigate")
def investigate(data: dict, db: Session = Depends(get_db)):
    """
    Perform an AI-assisted fraud investigation on a transaction.
    """

    transaction = data.get("transaction")

    device_hash = data.get("device_hash")

    report = investigate_transaction(
        db,
        transaction,
        device_hash
    )

    return report