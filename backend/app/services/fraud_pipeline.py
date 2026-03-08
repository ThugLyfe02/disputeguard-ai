from sqlalchemy.orm import Session

from app.services.fraud_signals import calculate_risk_score
from app.services.fraud_ml_prediction import predict_chargeback
from app.services.device_risk import detect_device_risk
from app.services.cross_merchant_intelligence import detect_cross_merchant_activity


def run_fraud_pipeline(db: Session, transaction: dict, device_hash: str):
    """
    Core fraud pipeline.

    This function aggregates signals from multiple fraud detection engines
    and returns a structured fraud analysis object.

    Fraud signals include:

    - rule-based risk scoring
    - device fingerprint intelligence
    - machine learning chargeback prediction
    - cross-merchant fraud intelligence
    """

    transaction_id = transaction.get("id")
    merchant_id = transaction.get("merchant_id")

    # --------------------------------------------------
    # Rule-based fraud signals
    # --------------------------------------------------

    rule_score = calculate_risk_score(
        db,
        transaction,
        transaction_id
    )

    # --------------------------------------------------
    # Device risk detection
    # --------------------------------------------------

    device_risk = detect_device_risk(
        db,
        device_hash,
        merchant_id
    )

    device_risk_score = device_risk.get("risk_score", 0)

    # --------------------------------------------------
    # Cross-merchant fraud intelligence
    # --------------------------------------------------

    cross_merchant = detect_cross_merchant_activity(
        db,
        device_hash
    )

    # --------------------------------------------------
    # Machine learning fraud prediction
    # --------------------------------------------------

    ml_prediction = predict_chargeback(
        amount=transaction.get("amount", 0),
        rule_score=rule_score,
        device_risk_score=device_risk_score,
        reputation_score=0,
        cluster_risk_score=0
    )

    # --------------------------------------------------
    # Final pipeline result
    # --------------------------------------------------

    return {
        "transaction_id": transaction_id,
        "rule_score": rule_score,
        "device_risk": device_risk,
        "ml_prediction": ml_prediction,
        "cross_merchant": cross_merchant
    }