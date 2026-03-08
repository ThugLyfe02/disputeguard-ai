"""
evidence_generator.py

Fraud Evidence Generator

Builds structured evidence packages for dispute responses and fraud
investigation workflows.

Evidence combines:

• Transaction data
• Fraud engine signals
• Graph intelligence
• Device intelligence
• Reputation signals
• ML predictions
• Timeline reconstruction

Used by:

• Fraud cases
• Dispute response automation
• Merchant dashboards
• Investigation tools
"""

from datetime import datetime


def generate_evidence(dispute: dict, transaction: dict, fraud_analysis: dict | None = None):
    """
    Generate structured fraud evidence.

    Parameters
    ----------
    dispute : dict
        Dispute record.

    transaction : dict
        Original transaction.

    fraud_analysis : dict | None
        Output of fraud_pipeline (optional but recommended).

    Returns
    -------
    dict
        Structured evidence package.
    """

    # --------------------------------------------------
    # Transaction Info
    # --------------------------------------------------

    transaction_id = transaction.get("id")
    amount = transaction.get("amount")
    customer_id = transaction.get("customer_id")
    email = transaction.get("email")
    merchant_id = transaction.get("merchant_id")

    # --------------------------------------------------
    # Dispute Info
    # --------------------------------------------------

    dispute_reason = dispute.get("reason")
    dispute_id = dispute.get("id")

    # --------------------------------------------------
    # Fraud Signals (from pipeline)
    # --------------------------------------------------

    fraud_scores = {}
    fraud_signals = {}

    if fraud_analysis:

        fraud_scores = fraud_analysis.get("scores", {})
        fraud_signals = fraud_analysis.get("signals", {})

    # --------------------------------------------------
    # Graph Intelligence
    # --------------------------------------------------

    graph_cluster = fraud_signals.get("graph_cluster", {})
    cross_merchant = fraud_signals.get("cross_merchant", {})
    network_analysis = fraud_signals.get("network_analysis", {})

    # --------------------------------------------------
    # Device Intelligence
    # --------------------------------------------------

    device_risk = fraud_signals.get("device_risk", {})

    # --------------------------------------------------
    # Reputation Intelligence
    # --------------------------------------------------

    reputation = fraud_signals.get("reputation", {})

    # --------------------------------------------------
    # ML Prediction
    # --------------------------------------------------

    ml_prediction = fraud_signals.get("ml_prediction", {})

    # --------------------------------------------------
    # Fraud Indicators
    # --------------------------------------------------

    fraud_indicators = []

    if fraud_scores.get("device_risk_score", 0) > 0.6:
        fraud_indicators.append("High device risk")

    if fraud_scores.get("cluster_risk_score", 0) > 0.6:
        fraud_indicators.append("Suspicious fraud cluster")

    if fraud_scores.get("network_risk_score", 0) > 0.6:
        fraud_indicators.append("Fraud network detected")

    if fraud_scores.get("fraud_network_score", 0) > 0.7:
        fraud_indicators.append("Fraud ring behavior")

    if fraud_scores.get("chargeback_probability", 0) > 0.7:
        fraud_indicators.append("High ML chargeback prediction")

    if fraud_scores.get("reputation_score", 0) < 0.3:
        fraud_indicators.append("Low reputation score")

    # --------------------------------------------------
    # Timeline Reconstruction
    # --------------------------------------------------

    timeline = [
        {
            "event": "payment_authorized",
            "timestamp": transaction.get("created_at"),
        },
        {
            "event": "order_processed",
            "timestamp": transaction.get("processed_at"),
        },
        {
            "event": "shipment_confirmed",
            "timestamp": transaction.get("shipped_at"),
        },
        {
            "event": "delivery_completed",
            "timestamp": transaction.get("delivered_at"),
        },
        {
            "event": "dispute_opened",
            "timestamp": dispute.get("created_at"),
        },
    ]

    # remove None timestamps
    timeline = [event for event in timeline if event["timestamp"]]

    # --------------------------------------------------
    # Evidence Package
    # --------------------------------------------------

    evidence = {

        "generated_at": datetime.utcnow().isoformat(),

        "transaction": {
            "transaction_id": transaction_id,
            "amount": amount,
            "customer_id": customer_id,
            "email": email,
            "merchant_id": merchant_id
        },

        "dispute": {
            "dispute_id": dispute_id,
            "reason": dispute_reason
        },

        "scores": fraud_scores,

        "signals": {
            "device_risk": device_risk,
            "graph_cluster": graph_cluster,
            "cross_merchant": cross_merchant,
            "network_analysis": network_analysis,
            "reputation": reputation,
            "ml_prediction": ml_prediction
        },

        "fraud_indicators": fraud_indicators,

        "timeline": timeline,

        "investigation_notes": {
            "cluster_size": len(graph_cluster) if isinstance(graph_cluster, list) else None,
            "device_risk_flag": fraud_scores.get("device_risk_score", 0) > 0.6,
            "network_risk_flag": fraud_scores.get("network_risk_score", 0) > 0.6
        }
    }

    return evidence