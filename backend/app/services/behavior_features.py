def extract_behavior_features(session):

    typing_score = min(session.get("typing_speed", 0) / 10, 1)

    mouse_entropy = session.get("mouse_entropy", 0)

    dwell_score = min(session.get("page_dwell_time", 0) / 30, 1)

    checkout_score = (
        1 if session.get("checkout_time", 0) < 5 else 0
    )

    return {
        "typing_score": typing_score,
        "mouse_entropy": mouse_entropy,
        "dwell_score": dwell_score,
        "checkout_score": checkout_score
    }