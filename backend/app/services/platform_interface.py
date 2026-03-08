from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.reputation_service import get_reputation
from app.services.graph_ml_detector import detect_graph_fraud
from app.services.global_intelligence import lookup_threat_indicator
from app.services.fraud_investigator import investigate_transaction
from app.services.fraud_defense_engine import autonomous_defense


def evaluate_transaction(db, transaction, device_hash):
    """
    Perform a full fraud evaluation using all fraud intelligence layers.
    """

    fraud_signals = run_fraud_pipeline(
        db,
        transaction,
        device_hash
    )

    device_reputation = get_reputation(
        db,
        "device",
        device_hash
    )

    graph_risk = detect_graph_fraud(device_hash)

    threat_lookup = lookup_threat_indicator(
        db,
        "device",
        device_hash
    )

    investigation = investigate_transaction(
        db,
        transaction,
        device_hash
    )

    defense = autonomous_defense(
        transaction,
        investigation
    )

    return {
        "transaction_id": transaction.get("id"),
        "fraud_signals": fraud_signals,
        "device_reputation": device_reputation,
        "graph_risk": graph_risk,
        "threat_intelligence": threat_lookup,
        "investigation_report": investigation,
        "defense_actions": defense
    }