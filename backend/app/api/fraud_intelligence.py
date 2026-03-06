from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.transaction import Transaction
from app.models.fraud_signal import FraudSignal
from app.services.fraud_features import extract_features
from app.services.fraud_model import predict_chargeback_probability

router = APIRouter()


@router.get("/transactions/{transaction_id}/risk")
def get_transaction_risk(transaction_id: int, db: Session = Depends(get_db)):

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()

    signals = db.query(FraudSignal).filter(
        FraudSignal.transaction_id == transaction_id
    ).all()

    features = extract_features(transaction, signals)

    prediction = predict_chargeback_probability(features)

    return prediction
