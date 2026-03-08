from app.models.fraud_features import FraudFeature


def store_features(
    db,
    transaction_id,
    merchant_id,
    amount,
    rule_score,
    device_risk_score,
    reputation_score,
    cluster_risk_score,
    chargeback_probability
):

    feature = FraudFeature(
        transaction_id=transaction_id,
        merchant_id=merchant_id,
        amount=amount,
        rule_score=rule_score,
        device_risk_score=device_risk_score,
        reputation_score=reputation_score,
        cluster_risk_score=cluster_risk_score,
        chargeback_probability=chargeback_probability
    )

    db.add(feature)
    db.commit()

    return feature


def get_training_data(db):

    records = db.query(FraudFeature).all()

    dataset = []

    for r in records:

        dataset.append({
            "amount": r.amount,
            "rule_score": r.rule_score,
            "device_risk_score": r.device_risk_score,
            "reputation_score": r.reputation_score,
            "cluster_risk_score": r.cluster_risk_score,
            "label": r.chargeback_probability
        })

    return dataset