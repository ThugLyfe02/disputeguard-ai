"""
evidence_generator.py

Chargeback Evidence Generator

Builds structured evidence packages for payment disputes using
fraud intelligence signals produced by the fraud pipeline.

Evidence includes:

• transaction details
• fraud risk scores
• graph intelligence
• device intelligence
• network indicators
• timeline reconstruction

The output can be sent directly to dispute APIs
(Stripe / Shopify / Adyen / PayPal).
"""


def generate_evidence(dispute: dict, transaction: dict, fraud_result: dict | None = None):
    """
    Generate structured chargeback evidence.
    """

    transaction_id = transaction.get("id")
    amount = transaction.get("amount")
    customer_id = transaction.get("customer_id")

    fraud_indicators = []
    fraud_scores = {}

    # --------------------------------------------------
    # Extract fraud intelligence signals
    # --------------------------------------------------

    if fraud_result:

        scores = fraud_result.get("scores", {})
        signals = fraud_result.get("signals", {})

        fraud_scores = scores

        device_risk = signals.get("device_risk", {})
        network_analysis = signals.get("network_analysis", {})
        fraud_network_analysis = signals.get("fraud_network_analysis", {})

        # Device reuse indicator
        if device_risk.get("device_reuse", False):
            fraud_indicators.append("Device reused across multiple transactions")

        # Graph cluster indicator
        cluster_size = fraud_network_analysis.get("cluster_size")
        if cluster_size and cluster_size > 5:
            fraud_indicators.append(f"Transaction belongs to fraud cluster of size {cluster_size}")

        # Cross merchant fraud indicator
        if network_analysis.get("cross_merchant", False):
            fraud_indicators.append("Device used across multiple merchants")

        # ML probability indicator
        chargeback_probability = scores.get("chargeback_probability", 0)
        if chargeback_probability > 0.7:
            fraud_indicators.append("High ML chargeback probability")

    # --------------------------------------------------
    # Construct Evidence Timeline
    # --------------------------------------------------

    timeline = [
        "Payment authorized",
        "Order processed",
        "Shipment confirmed",
        "Delivery completed"
    ]

    # --------------------------------------------------
    # Build Evidence Package
    # --------------------------------------------------

    evidence = {

        "transaction_id": transaction_id,
        "amount": amount,
        "customer_id": customer_id,

        "dispute_reason": dispute.get("reason"),

        "timeline": timeline,

        "fraud_scores": fraud_scores,

        "fraud_indicators": fraud_indicators,

        "recommendation": _recommendation(fraud_scores)
    }

    return evidence


# --------------------------------------------------
# Recommendation Engine
# --------------------------------------------------

def _recommendation(scores: dict):

    chargeback_probability = scores.get("chargeback_probability", 0)
    network_risk = scores.get("fraud_network_score", 0)

    if chargeback_probability > 0.8 or network_risk > 0.7:
        return "High likelihood of fraud"

    if chargeback_probability > 0.5:
        return "Moderate fraud risk"

    return "Low fraud risk"