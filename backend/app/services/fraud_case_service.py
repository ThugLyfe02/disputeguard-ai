from app.models.fraud_case import FraudCase


def create_fraud_case(
    db,
    transaction_id,
    merchant_id,
    risk_score,
    alert_type,
    fraud_analysis
):
    """
    Create a fraud investigation case.
    """

    priority = "low"

    if risk_score > 0.85:
        priority = "critical"
    elif risk_score > 0.65:
        priority = "high"
    elif risk_score > 0.45:
        priority = "medium"

    case = FraudCase(
        transaction_id=transaction_id,
        merchant_id=merchant_id,
        risk_score=risk_score,
        alert_type=alert_type,
        fraud_analysis=fraud_analysis,
        case_priority=priority
    )

    db.add(case)
    db.commit()

    return case