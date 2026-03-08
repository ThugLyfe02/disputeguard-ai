from datetime import datetime


def build_fraud_report(entity: str, signals: dict, explanations: list):
    """
    Creates a structured fraud investigation report.
    """

    risk_score = signals.get("ml_prediction", {}).get(
        "chargeback_probability", 0
    )

    if risk_score > 0.8:
        risk_level = "high"
    elif risk_score > 0.5:
        risk_level = "medium"
    else:
        risk_level = "low"

    recommended_actions = []

    if risk_level == "high":
        recommended_actions.extend([
            "Block transaction immediately",
            "Trigger manual review",
            "Flag associated device and customer"
        ])

    elif risk_level == "medium":
        recommended_actions.extend([
            "Require additional verification",
            "Monitor account activity"
        ])

    else:
        recommended_actions.append(
            "Transaction appears safe but continue monitoring"
        )

    return {
        "entity": entity,
        "investigation_timestamp": datetime.utcnow().isoformat(),
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level,
        "fraud_signals": signals,
        "explanations": explanations,
        "recommended_actions": recommended_actions
    }