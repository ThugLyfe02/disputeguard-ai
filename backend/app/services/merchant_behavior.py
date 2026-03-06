from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction
from app.models.dispute import Dispute
from app.models.fraud_signal import FraudSignal


def analyze_merchant_behavior(db: Session, merchant_id: int):

    total_transactions = db.query(Transaction).filter(
        Transaction.merchant_id == merchant_id
    ).count()

    total_disputes = db.query(Dispute).filter(
        Dispute.merchant_id == merchant_id
    ).count()

    dispute_rate = (
        total_disputes / total_transactions
        if total_transactions > 0 else 0
    )

    fraud_signal_count = db.query(FraudSignal).filter(
        FraudSignal.merchant_id == merchant_id
    ).count()

    total_disputed_amount = db.query(
        func.sum(Dispute.amount)
    ).filter(
        Dispute.merchant_id == merchant_id
    ).scalar()

    return {
        "merchant_id": merchant_id,
        "total_transactions": total_transactions,
        "total_disputes": total_disputes,
        "dispute_rate": round(dispute_rate, 3),
        "fraud_signals_detected": fraud_signal_count,
        "total_disputed_amount": total_disputed_amount or 0
    }
