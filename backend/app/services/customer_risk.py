from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.dispute import Dispute


def calculate_customer_risk(db: Session, customer_id: str):

    transactions = db.query(Transaction).filter(
        Transaction.customer_id == customer_id
    ).count()

    disputes = db.query(Dispute).filter(
        Dispute.transaction_id == customer_id
    ).count()

    dispute_rate = disputes / transactions if transactions else 0

    return {
        "customer_id": customer_id,
        "transactions": transactions,
        "disputes": disputes,
        "dispute_rate": round(dispute_rate, 3),
        "risk_level": (
            "high" if dispute_rate > 0.3
            else "medium" if dispute_rate > 0.1
            else "low"
        )
    }
