def predict_dispute_win_probability(dispute: dict, fraud_signals: list):

    score = 0.5  # baseline probability

    reason = dispute.get("reason")

    if reason == "fraudulent":
        score += 0.1

    if reason == "product_not_received":
        score -= 0.15

    # Penalize for high number of fraud signals
    if fraud_signals:
        score -= min(len(fraud_signals) * 0.05, 0.25)

    # Clamp between 0 and 1
    score = max(0, min(score, 1))

    return {
        "win_probability": round(score, 2),
        "risk_level": "high" if score < 0.4 else "medium" if score < 0.7 else "low"
    }
