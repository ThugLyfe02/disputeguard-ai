from app.services.behavior_features import extract_behavior_features


def detect_behavior_risk(session):

    features = extract_behavior_features(session)

    risk_score = (
        features["typing_score"] * 0.3 +
        features["checkout_score"] * 0.3 +
        (1 - features["mouse_entropy"]) * 0.2 +
        (1 - features["dwell_score"]) * 0.2
    )

    if risk_score > 0.75:
        level = "high"
    elif risk_score > 0.4:
        level = "medium"
    else:
        level = "low"

    return {
        "behavior_risk_score": round(risk_score, 3),
        "behavior_risk_level": level,
        "features": features
    }