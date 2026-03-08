from app.models.global_fraud_signal import GlobalFraudSignal


def update_global_signal(db, entity_type, entity_id, merchant_id, is_dispute):

    signal = (
        db.query(GlobalFraudSignal)
        .filter(
            GlobalFraudSignal.entity_type == entity_type,
            GlobalFraudSignal.entity_id == entity_id
        )
        .first()
    )

    if not signal:

        signal = GlobalFraudSignal(
            entity_type=entity_type,
            entity_id=entity_id,
            merchant_count=1,
            dispute_count=0,
            global_risk_score=0
        )

        db.add(signal)

    else:

        signal.merchant_count += 1

    if is_dispute:
        signal.dispute_count += 1

    dispute_ratio = (
        signal.dispute_count / signal.merchant_count
        if signal.merchant_count else 0
    )

    signal.global_risk_score = min(dispute_ratio * 2, 1)

    db.commit()

    return signal