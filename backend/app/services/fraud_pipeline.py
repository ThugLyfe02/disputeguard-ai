from sqlalchemy.orm import Session

from app.services.reputation_service import get_reputation
from app.services.feature_store import store_features
from app.services.fraud_alerts import generate_alert
from app.services.fraud_stream import fraud_stream

from app.risk_engines.rule_engine import RuleEngine
from app.risk_engines.device_engine import DeviceEngine
from app.risk_engines.ml_engine import MLEngine
from app.risk_engines.graph_engine import GraphEngine
from app.risk_engines.cross_merchant_engine import CrossMerchantEngine
from app.services.risk_orchestrator import RiskOrchestrator


def run_fraud_pipeline(db: Session, transaction: dict, device_hash: str):
    """
    Core fraud intelligence pipeline.

    This function aggregates multiple fraud intelligence signals and produces
    a structured fraud risk evaluation.

    The pipeline combines:

        • Rule-based fraud signals (via RuleEngine)
        • Device fingerprint intelligence (via DeviceEngine)
        • Fraud graph cluster analysis (via GraphEngine)
        • Cross-merchant fraud detection (via CrossMerchantEngine)
        • Machine learning chargeback prediction (via MLEngine)
        • Entity reputation scoring (direct call, not yet an engine)

    Engines are executed by :class:`~app.services.risk_orchestrator.RiskOrchestrator`
    in sequence.  Each engine's score is accumulated in the shared context so
    later engines (e.g. MLEngine) can consume upstream signals.

    All extracted signals are stored in the feature store to support
    model retraining and fraud analytics.
    """

    transaction_id = transaction.get("id")
    merchant_id = transaction.get("merchant_id")
    amount = transaction.get("amount", 0)

    # ----------------------------------------------------
    # 1–5. Plugin-Based Risk Engine Orchestration
    # ----------------------------------------------------

    context = {
        "transaction": transaction,
        "merchant_id": merchant_id,
        "device_hash": device_hash,
    }

    orchestrator = RiskOrchestrator(engines=[
        RuleEngine(),
        DeviceEngine(),
        GraphEngine(),
        CrossMerchantEngine(),
        MLEngine(),
    ])

    orchestrator_result = orchestrator.evaluate(db, context)

    engine_results = orchestrator_result["engines"]
    engine_scores = orchestrator_result["scores"]

    # Convenience aliases for downstream steps (feature store, alerts, stream).
    rule_score = engine_scores.get("rule_engine", 0)
    device_risk = engine_results.get("device_engine", {}).get("details", {})
    device_risk_score = engine_scores.get("device_engine", 0)
    cross_merchant = engine_results.get("cross_merchant_engine", {}).get("details", {})
    graph_cluster = engine_results.get("graph_engine", {}).get("details", {})
    cluster_risk_score = engine_scores.get("graph_engine", 0)
    ml_prediction = engine_results.get("ml_engine", {}).get("details", {})
    chargeback_probability = engine_scores.get("ml_engine", 0)

    # ----------------------------------------------------
    # 6. Reputation Intelligence
    # ----------------------------------------------------

    reputation = get_reputation(
        db,
        entity_type="device",
        entity_id=device_hash
    )

    reputation_score = reputation.get("reputation_score", 0)

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
        "ml_prediction": ml_prediction,
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
        "alert": alert,
        "orchestrator": orchestrator_result,
    }