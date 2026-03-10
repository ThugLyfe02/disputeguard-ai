"""
fraud_pipeline.py

Core fraud intelligence pipeline.

Pipeline stages:

transaction
    ↓
fraud graph expansion
    ↓
temporal graph update
    ↓
graph signal worker trigger
    ↓
risk engines
    ↓
graph feature extraction
    ↓
reputation intelligence
    ↓
feature store
    ↓
alerts
    ↓
event bus + fraud stream
"""

from sqlalchemy.orm import Session
import uuid

from app.services.reputation_service import get_reputation
from app.services.feature_store import store_features
from app.services.fraud_alerts import generate_alert

from app.services.event_bus import event_bus
from app.services.fraud_stream import fraud_stream

from app.services.fraud_network_graph import fraud_graph
from app.services.temporal_graph import temporal_graph

from app.risk_engines.rule_engine import RuleEngine
from app.risk_engines.device_engine import DeviceEngine
from app.risk_engines.graph_engine import GraphEngine
from app.risk_engines.cross_merchant_engine import CrossMerchantEngine
from app.risk_engines.network_engine import NetworkEngine
from app.risk_engines.fraud_network_engine import FraudNetworkEngine
from app.risk_engines.graph_feature_engine import GraphFeatureEngine
from app.risk_engines.ml_engine import MLEngine

from app.services.risk_orchestrator import RiskOrchestrator


def run_fraud_pipeline(db: Session, transaction: dict, device_hash: str):

    # --------------------------------------------------
    # Event ID
    # --------------------------------------------------

    event_id = str(uuid.uuid4())

    # --------------------------------------------------
    # Extract transaction attributes
    # --------------------------------------------------

    transaction_id = transaction.get("id")
    merchant_id = transaction.get("merchant_id")
    amount = transaction.get("amount", 0)

    tx_node = f"tx_{transaction_id}"
    device_node = f"device_{device_hash}"
    merchant_node = f"merchant_{merchant_id}"

    # --------------------------------------------------
    # Expand Fraud Graph
    # --------------------------------------------------

    fraud_graph.build_graph_from_transaction(
        transaction,
        device_hash,
        merchant_id
    )

    # --------------------------------------------------
    # Temporal Graph Update
    # --------------------------------------------------
    # Temporal edges are recorded by fraud_graph.add_edge() inside
    # build_graph_from_transaction().  No explicit call needed here.

    # --------------------------------------------------
    # Trigger Graph Signal Worker
    # --------------------------------------------------

    event_bus.publish(
        "graph.node.updated",
        {"node": tx_node}
    )

    # --------------------------------------------------
    # Evaluation Context
    # --------------------------------------------------

    context = {
        "transaction": transaction,
        "merchant_id": merchant_id,
        "device_hash": device_hash,
        "transaction_id": transaction_id
    }

    # --------------------------------------------------
    # Risk Engine Orchestration
    # --------------------------------------------------

    orchestrator = RiskOrchestrator([
        RuleEngine(),
        DeviceEngine(),
        GraphEngine(),
        CrossMerchantEngine(),
        NetworkEngine(),
        FraudNetworkEngine(),
        GraphFeatureEngine(),
        MLEngine(),
    ])

    orchestrator_result = orchestrator.evaluate(db, context)

    engine_results = orchestrator_result.get("engines", {})
    engine_scores = orchestrator_result.get("scores", {})

    # --------------------------------------------------
    # Convenience Aliases
    # --------------------------------------------------

    rule_score = engine_scores.get("rule_engine", 0)

    device_risk = engine_results.get("device_engine", {}).get("details", {})
    device_risk_score = engine_scores.get("device_engine", 0)

    graph_cluster = engine_results.get("graph_engine", {}).get("details", {})
    cluster_risk_score = engine_scores.get("graph_engine", 0)

    cross_merchant = engine_results.get("cross_merchant_engine", {}).get("details", {})

    network_analysis = engine_results.get("network_engine", {}).get("details", {})
    network_risk_score = engine_scores.get("network_engine", 0)

    fraud_network_analysis = engine_results.get("fraud_network_engine", {}).get("details", {})
    fraud_network_score = engine_scores.get("fraud_network_engine", 0)

    graph_features = engine_results.get("graph_feature_engine", {}).get("details", {})

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
    # Store ML Features
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
        network_risk_score=network_risk_score,
        fraud_network_score=fraud_network_score,
        chargeback_probability=chargeback_probability,
        **graph_features
    )

    # --------------------------------------------------
    # Build Fraud Result
    # --------------------------------------------------

    fraud_result = {

        "event_id": event_id,
        "transaction_id": transaction_id,
        "merchant_id": merchant_id,

        "scores": {
            "rule_score": rule_score,
            "device_risk_score": device_risk_score,
            "cluster_risk_score": cluster_risk_score,
            "network_risk_score": network_risk_score,
            "fraud_network_score": fraud_network_score,
            "chargeback_probability": chargeback_probability,
            "reputation_score": reputation_score
        },

        "signals": {
            "device_risk": device_risk,
            "graph_cluster": graph_cluster,
            "cross_merchant": cross_merchant,
            "network_analysis": network_analysis,
            "fraud_network_analysis": fraud_network_analysis,
            "graph_features": graph_features,
            "reputation": reputation,
            "ml_prediction": ml_prediction
        }
    }

    # --------------------------------------------------
    # Alert Generation
    # --------------------------------------------------

    alert = generate_alert(fraud_result)
    fraud_result["alert"] = alert

    # --------------------------------------------------
    # Publish Events
    # --------------------------------------------------

    event_payload = {
        "event_id": event_id,
        "transaction_id": transaction_id,
        "merchant_id": merchant_id,
        "fraud_result": fraud_result
    }

    event_bus.publish(
        "fraud.analysis.completed",
        event_payload
    )

    fraud_stream.publish(
        "fraud_analysis_completed",
        event_payload
    )

    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "event_id": event_id,
        "transaction_id": transaction_id,
        "fraud_analysis": fraud_result,
        "orchestrator": orchestrator_result
    }