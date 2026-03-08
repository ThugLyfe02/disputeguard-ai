from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.platform_interface import evaluate_transaction

router = APIRouter()


@router.post("/fraud/platform/evaluate")
def evaluate(data: dict, db: Session = Depends(get_db)):
    """
    Full fraud intelligence evaluation endpoint.
    """

    transaction = data.get("transaction")
    device_hash = data.get("device_hash")

    result = evaluate_transaction(
        db,
        transaction,
        device_hash
    )

    return result