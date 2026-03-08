from app.models.global_fraud_signal import GlobalFraudSignal


def get_global_risk(db, entity_type, entity_id):

    signal = (
        db.query(GlobalFraudSignal)
        .filter(
            GlobalFraudSignal.entity_type == entity_type,
            GlobalFraudSignal.entity_id == entity_id
        )
        .first()
    )

    if not signal:
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "global_risk_score": 0
        }

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "merchant_count": signal.merchant_count,
        "dispute_count": signal.dispute_count,
        "global_risk_score": signal.global_risk_score
    }