from typing import Dict, List


def explain_fraud_signals(signals: Dict) -> List[str]:
    """
    Converts raw fraud signals into human-readable explanations.
    This is useful for investigators and audit logs.
    """

    explanations = []

    if signals.get("rule_score", 0) > 0.5:
        explanations.append(
            "Rule-based fraud detection triggered multiple signals."
        )

    device_risk = signals.get("device_risk", {})
    if device_risk.get("risk_level") == "high":
        explanations.append(
            f"Device fingerprint has high historical usage "
            f"({device_risk.get('usage_count')} transactions)."
        )

    ml_prediction = signals.get("ml_prediction", {})
    if ml_prediction.get("chargeback_probability", 0) > 0.7:
        explanations.append(
            "Machine learning model predicts a high probability of chargeback."
        )

    if signals.get("cluster_risk_score", 0) > 0.6:
        explanations.append(
            "Transaction is linked to a high-risk fraud cluster."
        )

    if signals.get("reputation_score", 0) > 0.6:
        explanations.append(
            "Entity reputation score indicates historical fraud activity."
        )

    if not explanations:
        explanations.append(
            "No strong fraud signals detected. Risk appears low."
        )

    return explanations