from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.services.fraud_signals import calculate_risk_score


def create_transaction(db: Session, stripe_event: dict):
    data = stripe_event.get("data", {}).get("object", {})

    transaction = Transaction(
        merchant_id=data.get("merchant_id", "unknown"),
        customer_id=data.get("customer", "unknown"),
        amount=data.get("amount", 0) / 100 if data.get("amount") else 0,
        currency=data.get("currency", "usd"),
        status=data.get("status", "unknown"),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Run fraud scoring
    risk_score = calculate_risk_score(data)

    return {
        "transaction_id": transaction.id,
        "risk_score": risk_score
    }
