from sqlalchemy.orm import Session

from app.services.fraud_signals import calculate_risk_score
from app.services.device_risk import detect_device_risk
from app.services.cross_merchant_intelligence import detect_cross_merchant_activity
from app.services.fraud_ml_prediction import predict_chargeback
from app.services.reputation_service import get_reputation
from app.services.fraud_graph_analysis import analyze_entity_cluster
from app.services.global_intelligence import get_global_risk


def run_fraud_pipeline(db: Session, transaction, device_hash):
    """
    Core fraud intelligence pipeline.

    Combines multiple detection systems into a unified
    fraud analysis object.

    Signals include:

    - rule-based fraud scoring
    - device fingerprint intelligence
    - cross-merchant fraud intelligence
    - entity reputation scoring
    - fraud graph cluster detection
    - machine learning chargeback prediction
    """

    transaction_id = transaction.get("id")
    merchant_id = transaction.get("merchant_id")

    # -----------------------------
    # Rule Engine
    # -----------------------------

    rule_score = calculate_risk_score(
        db,
        transaction,
        transaction_id
    )

    # -----------------------------
    # Device Intelligence
    # -----------------------------

    device_risk = detect_device_risk(
        db,
        device_hash,
        merchant_id
    )

    device_risk_score = device_risk.get("usage_count", 0)

    # -----------------------------
    # Cross-Merchant Intelligence
    # -----------------------------

    cross_merchant = detect_cross_merchant_activity(
        db,
        device_hash
    )

    # -----------------------------
    # Reputation System
    # -----------------------------

    reputation = get_reputation(
        db,
        "device",
        device_hash
    )

    reputation_score = reputation.get("reputation_score", 0)

    # -----------------------------
    # Fraud Graph Cluster Analysis
    # -----------------------------

    graph_analysis = analyze_entity_cluster(
        db,
        f"device_{device_hash}"
    )

    cluster_risk_score = graph_analysis.get("cluster_risk_score", 0)

    # -----------------------------
    # Global Intelligence
    # -----------------------------

    global_intel = get_global_risk(
        db,
        "device",
        device_hash
    )

    # -----------------------------
    # Machine Learning Prediction
    # -----------------------------

    ml_prediction = predict_chargeback(
        amount=transaction.get("amount", 0),
        rule_score=rule_score,
        device_risk_score=device_risk_score,
        reputation_score=reputation_score,
        cluster_risk_score=cluster_risk_score
    )

    # -----------------------------
    # Final Result
    # -----------------------------

    return {
        "transaction_id": transaction_id,
        "rule_score": rule_score,
        "device_risk": device_risk,
        "cross_merchant": cross_merchant,
        "reputation": reputation,
        "fraud_graph": graph_analysis,
        "global_intelligence": global_intel,
        "ml_prediction": ml_prediction
    }