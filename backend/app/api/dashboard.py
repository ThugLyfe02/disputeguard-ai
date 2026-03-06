from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db
from app.auth_dependency import get_current_merchant

from app.models.dispute import Dispute
from app.models.fraud_signal import FraudSignal
from app.models.transaction import Transaction

router = APIRouter()


@router.get("/dashboard/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    merchant_id: int = Depends(get_current_merchant)
):

    total_transactions = db.query(Transaction).filter(
        Transaction.merchant_id == merchant_id
    ).count()

    total_disputes = db.query(Dispute).filter(
        Dispute.merchant_id == merchant_id
    ).count()

    open_disputes = db.query(Dispute).filter(
        Dispute.merchant_id == merchant_id,
        Dispute.status == "open"
    ).count()

    total_disputed_amount = db.query(
        func.sum(Dispute.amount)
    ).filter(
        Dispute.merchant_id == merchant_id
    ).scalar()

    fraud_signal_count = db.query(FraudSignal).filter(
        FraudSignal.merchant_id == merchant_id
    ).count()

    return {
        "total_transactions": total_transactions,
        "total_disputes": total_disputes,
        "open_disputes": open_disputes,
        "total_disputed_amount": total_disputed_amount or 0,
        "fraud_signals_detected": fraud_signal_count
    }
