from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.dispute import Dispute
from app.models.fraud_signal import FraudSignal
from app.services.dispute_prediction import predict_dispute_win_probability

router = APIRouter()


@router.get("/disputes/{dispute_id}/prediction")
def predict_dispute_outcome(dispute_id: int, db: Session = Depends(get_db)):

    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()

    if not dispute:
        return {"message": "Dispute not found"}

    signals = db.query(FraudSignal).filter(
        FraudSignal.transaction_id == dispute.transaction_id
    ).all()

    prediction = predict_dispute_win_probability(
        {
            "reason": dispute.reason
        },
        signals
    )

    return prediction
