"""
fraud_pipeline.py

Core fraud intelligence pipeline.

This pipeline orchestrates multiple fraud detection engines and produces
a structured fraud analysis result.

Architecture:

transaction → risk engines → reputation → feature store → alerts → event bus
"""

from sqlalchemy.orm import Session

from app.services.reputation_service import get_reputation
from app.services.feature_store import store_features
from app.services.fraud_alerts import generate_alert

from app.services.event_bus import event_bus
from app.services.fraud_stream import fraud_stream
from app.services.fraud_network_graph import fraud_graph

from app.risk_engines.rule_engine import RuleEngine
from app.risk_engines.device_engine import DeviceEngine
from app.risk_engines.ml_engine import MLEngine
from app.risk_engines.graph_engine import GraphEngine
from app.risk_engines.cross_merchant_engine import CrossMerchantEngine

from app.services.risk_orchestrator import RiskOrchestrator


def run_fraud_pipeline(db: Session, transaction: dict, device_hash: str):
    """
    Execute the DisputeGuard AI fraud intelligence pipeline.
    """

    # --------------------------------------------------
    # Extract transaction attributes
    # --------------------------------------------------

    transaction_id = transaction.get("id")
    merchant_id = transaction.get("merchant_id")
    amount = transaction.get("amount", 0)

    # --------------------------------------------------
    # Build evaluation context
    # --------------------------------------------------

    context = {
        "transaction": transaction,
        "merchant_id": merchant_id,
        "device_hash": device_hash,
    }

    # --------------------------------------------------
    # Run Plugin-Based Risk Engines
    # --------------------------------------------------

    orchestrator = RiskOrchestrator([
        RuleEngine(),
        DeviceEngine(),
        GraphEngine(),
        CrossMerchantEngine(),
        MLEngine(),
    ])

    orchestrator_result = orchestrator.evaluate(db, context)

    engine_results = orchestrator_result.get("engines", {})
    engine_scores = orchestrator_result.get("scores", {})

    # --------------------------------------------------
    # Expand Fraud Intelligence Graph
    # --------------------------------------------------

    fraud_graph.build_graph_from_transaction(
        transaction,
        device_hash,
        merchant_id
    )

    # --------------------------------------------------
    # Convenience Aliases
    # --------------------------------------------------

    rule_score = engine_scores.get("rule_engine", 0)

    device_risk = engine_results.get("device_engine", {}).get("details", {})
    device_risk_score = engine_scores.get("device_engine", 0)

    graph_cluster = engine_results.get("graph_engine", {}).get("details", {})
    cluster_risk_score = engine_scores.get("graph_engine", 0)

    cross_merchant = engine_results.get("cross_merchant_engine", {}).get("details", {})

    ml_prediction = engine_results.get("ml_engine", {}).get("details", {})
    chargeback_probability = engine_scores.get("ml_engine", 0)

    # --------------------------------------------------
    # Reputation Intelligence
    # --------------------------------------------------

    reputation = get_reputation(
        db,
        entity_type="device",
        entity_id=device_hash
    )

    reputation_score = reputation.get("reputation_score", 0)

    # --------------------------------------------------
    # Store Features for ML Training
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Build Fraud Result
    # --------------------------------------------------

    fraud_result = {
        "transaction_id": transaction_id,
        "merchant_id": merchant_id,
        "rule_score": rule_score,
        "device_risk": device_risk,
        "graph_cluster": graph_cluster,
        "cross_merchant": cross_merchant,
        "reputation": reputation,
        "ml_prediction": ml_prediction
    }

    # --------------------------------------------------
    # Alert Generation
    # --------------------------------------------------

    alert = generate_alert(fraud_result)

    fraud_result["alert"] = alert

    # --------------------------------------------------
    # Publish Event to Event Bus
    # --------------------------------------------------

    event_bus.publish(
        "fraud.analysis.completed",
        fraud_result
    )

    fraud_stream.publish("fraud_analysis_completed", fraud_result)

    # --------------------------------------------------
    # Final Response
    # --------------------------------------------------

    return {
        "transaction_id": transaction_id,
        "fraud_analysis": fraud_result,
        "orchestrator": orchestrator_result
    }