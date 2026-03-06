import random


def predict_chargeback_probability(features):

    score = 0.5

    if features["high_amount"]:
        score += 0.2

    if features["ip_mismatch"]:
        score += 0.2

    score += min(features["signal_count"] * 0.05, 0.2)

    score = max(0, min(score, 1))

    return {
        "chargeback_probability": round(score, 2),
        "risk_level": "high" if score > 0.75 else "medium" if score > 0.4 else "low"
    }
