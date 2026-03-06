from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.fraud_signal import FraudSignal

router = APIRouter()


@router.get("/transactions/{transaction_id}/fraud-signals")
def get_fraud_signals(transaction_id: str, db: Session = Depends(get_db)):

    signals = db.query(FraudSignal).filter(
        FraudSignal.transaction_id == transaction_id
    ).all()

    return signals
