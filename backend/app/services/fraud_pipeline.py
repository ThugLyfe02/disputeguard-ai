from sqlalchemy.orm import Session

from app.services.fraud_signals import calculate_risk_score
from app.services.device_risk import detect_device_risk
from app.services.cross_merchant_intelligence import detect_cross_merchant_activity
from app.services.fraud_ml_prediction import predict_chargeback
from app.services.reputation_service import get_reputation
from app.services.fraud_graph_analysis import analyze_entity_cluster
from app.services.feature_store import store_features
from app.services.fraud_alerts import generate_alert

from app.services.fraud_stream import fraud_stream


def run_fraud_pipeline(db: Session, transaction: dict, device_hash: str):
    """
    Core fraud intelligence pipeline.

    This function aggregates multiple fraud intelligence signals and produces
    a structured fraud risk evaluation.

    The pipeline combines:

        • Rule-based fraud signals
        • Device fingerprint intelligence
        • Cross-merchant fraud detection
        • Entity reputation scoring
        • Fraud graph cluster analysis
        • Machine learning chargeback prediction

    All extracted signals are stored in the feature store to support
    model retraining and fraud analytics.
    """

    transaction_id = transaction.get("id")
    merchant_id = transaction.get("merchant_id")
    amount = transaction.get("amount", 0)

    # ----------------------------------------------------
    # 1. Rule-Based Fraud Signals
    # ----------------------------------------------------

    rule_score = calculate_risk_score(
        db,
        transaction,
        transaction_id
    )

    # ----------------------------------------------------
    # 2. Device Fingerprint Risk
    # ----------------------------------------------------

    device_risk = detect_device_risk(
        db,
        device_hash,
        merchant_id
    )

    device_risk_score = device_risk.get("risk_level_score", 0)

    # ----------------------------------------------------
    # 3. Cross-Merchant Fraud Intelligence
    # ----------------------------------------------------

    cross_merchant = detect_cross_merchant_activity(
        db,
        device_hash
    )

    cross_merchant_score = cross_merchant.get("risk_score", 0)

    # ----------------------------------------------------
    # 4. Reputation Intelligence
    # ----------------------------------------------------

    reputation = get_reputation(
        db,
        entity_type="device",
        entity_id=device_hash
    )

    reputation_score = reputation.get("reputation_score", 0)

    # ----------------------------------------------------
    # 5. Fraud Graph Cluster Intelligence
    # ----------------------------------------------------

    graph_cluster = analyze_entity_cluster(
        db,
        entity=device_hash
    )

    cluster_risk_score = graph_cluster.get("cluster_risk_score", 0)

    # ----------------------------------------------------
    # 6. Machine Learning Chargeback Prediction
    # ----------------------------------------------------

    ml_prediction = predict_chargeback(
        amount=amount,
        rule_score=rule_score,
        device_risk_score=device_risk_score,
        reputation_score=reputation_score,
        cluster_risk_score=cluster_risk_score
    )

    chargeback_probability = ml_prediction.get(
        "chargeback_probability",
        0
    )

    # ----------------------------------------------------
    # 7. Store Features For Model Training
    # ----------------------------------------------------

    store_features(
        db=db,
        transaction_id=transaction_id,
        merchant_id=merchant_id,
        amount=amount,
        rule_score=rule_score,
        device_risk_score=device_risk_score,
        reputation_score=reputation_score,
        cluster_risk_score=cluster_risk_score,
        chargeback_probability=chargeback_probability
    )

    # ----------------------------------------------------
    # 8. Fraud Alert Generation
    # ----------------------------------------------------

    fraud_result = {
        "transaction_id": transaction_id,
        "rule_score": rule_score,
        "device_risk": device_risk,
        "cross_merchant": cross_merchant,
        "reputation": reputation,
        "graph_cluster": graph_cluster,
        "ml_prediction": ml_prediction
    }

    alert = generate_alert(fraud_result)

    # ----------------------------------------------------
    # 9. Publish Event To Fraud Stream
    # ----------------------------------------------------

    fraud_stream.publish(
        "fraud_analysis_completed",
        fraud_result
    )

    # ----------------------------------------------------
    # Final Structured Result
    # ----------------------------------------------------

    return {
        "transaction_id": transaction_id,
        "rule_score": rule_score,
        "device_risk": device_risk,
        "cross_merchant": cross_merchant,
        "reputation": reputation,
        "graph_cluster": graph_cluster,
        "ml_prediction": ml_prediction,
        "alert": alert
    }