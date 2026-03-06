from sqlalchemy.orm import Session
from app.services.fraud_signal_service import store_fraud_signal


def calculate_risk_score(db: Session, transaction: dict, transaction_id: str):

    risk_score = 0

    amount = transaction.get("amount", 0)

    # High transaction amount signal
    if amount > 100000:  # Stripe sends amounts in cents
        risk_score += 30
        store_fraud_signal(
            db,
            transaction_id,
            "high_amount",
            "Transaction amount significantly higher than normal"
        )

    # IP mismatch signal
    ip_country = transaction.get("ip_country")
    billing_country = transaction.get("billing_country")

    if ip_country and billing_country and ip_country != billing_country:
        risk_score += 25
        store_fraud_signal(
            db,
            transaction_id,
            "ip_mismatch",
            "Billing country does not match IP location"
        )

    return risk_score
