from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction
from app.models.dispute import Dispute
from app.models.device_fingerprint import DeviceFingerprint
from app.models.reputation import Reputation
from app.models.fraud_case import FraudCase
from app.models.global_fraud_signal import GlobalFraudSignal


def system_overview(db: Session):

    total_transactions = db.query(Transaction).count()

    total_disputes = db.query(Dispute).count()

    dispute_rate = (
        total_disputes / total_transactions
        if total_transactions else 0
    )

    open_cases = (
        db.query(FraudCase)
        .filter(FraudCase.status == "open")
        .count()
    )

    return {
        "transactions": total_transactions,
        "disputes": total_disputes,
        "dispute_rate": round(dispute_rate, 3),
        "open_cases": open_cases
    }


def fraud_heatmap(db: Session):

    results = (
        db.query(
            Dispute.merchant_id,
            func.count(Dispute.id).label("dispute_count")
        )
        .group_by(Dispute.merchant_id)
        .all()
    )

    return [
        {
            "merchant_id": r.merchant_id,
            "dispute_count": r.dispute_count
        }
        for r in results
    ]


def high_risk_entities(db: Session):

    entities = (
        db.query(Reputation)
        .order_by(Reputation.reputation_score.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "entity_type": e.entity_type,
            "entity_id": e.entity_id,
            "risk_score": e.reputation_score
        }
        for e in entities
    ]


def global_threat_overview(db: Session):

    signals = (
        db.query(GlobalFraudSignal)
        .order_by(GlobalFraudSignal.global_risk_score.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "entity_type": s.entity_type,
            "entity_id": s.entity_id,
            "risk_score": s.global_risk_score,
            "merchant_count": s.merchant_count
        }
        for s in signals
    ]