from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db
from app.models.dispute import Dispute
from app.models.fraud_signal import FraudSignal
from app.models.transaction import Transaction

router = APIRouter()


@router.get("/dashboard/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):

    total_transactions = db.query(Transaction).count()

    total_disputes = db.query(Dispute).count()

    open_disputes = db.query(Dispute).filter(
        Dispute.status == "open"
    ).count()

    total_disputed_amount = db.query(
        func.sum(Dispute.amount)
    ).scalar()

    fraud_signal_count = db.query(FraudSignal).count()

    return {
        "total_transactions": total_transactions,
        "total_disputes": total_disputes,
        "open_disputes": open_disputes,
        "total_disputed_amount": total_disputed_amount or 0,
        "fraud_signals_detected": fraud_signal_count
    }
