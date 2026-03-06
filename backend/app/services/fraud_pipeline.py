from app.services.fraud_signals import calculate_risk_score
from app.services.fraud_ml_prediction import predict_chargeback
from app.services.device_risk import detect_device_risk


def run_fraud_pipeline(db, transaction, device_hash):

    risk_score = calculate_risk_score(
        db,
        transaction,
        transaction.get("id")
    )

    device_risk = detect_device_risk(db, device_hash)

    ml_prediction = predict_chargeback(
        transaction.get("amount"),
        risk_score
    )

    return {
        "rule_score": risk_score,
        "device_risk": device_risk,
        "ml_prediction": ml_prediction
    }
