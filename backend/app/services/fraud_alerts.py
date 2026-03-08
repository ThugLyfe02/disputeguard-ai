from app.services.fraud_case_service import create_fraud_case


def generate_alert(db, fraud_result):
    """
    Generate fraud alert and optionally create case.
    """

    probability = fraud_result["ml_prediction"]["chargeback_probability"]

    alert = None

    if probability > 0.8:
        alert = "HIGH_RISK_TRANSACTION"

    elif probability > 0.5:
        alert = "MEDIUM_RISK_TRANSACTION"

    if alert:

        create_fraud_case(
            db=db,
            transaction_id=fraud_result["transaction_id"],
            merchant_id=fraud_result.get("merchant_id"),
            risk_score=probability,
            alert_type=alert,
            fraud_analysis=fraud_result
        )

    return {
        "alert": alert,
        "risk_probability": probability
    }