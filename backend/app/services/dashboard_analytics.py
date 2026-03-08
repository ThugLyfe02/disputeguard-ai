from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction
from app.models.dispute import Dispute
from app.models.device_fingerprint import DeviceFingerprint
from app.models.reputation import Reputation
from app.models.global_fraud_signal import GlobalFraudSignal


def fraud_overview(db: Session):

    total_transactions = db.query(Transaction).count()

    total_disputes = db.query(Dispute).count()

    dispute_rate = (
        total_disputes / total_transactions
        if total_transactions else 0
    )

    return {
        "total_transactions": total_transactions,
        "total_disputes": total_disputes,
        "dispute_rate": round(dispute_rate, 3)
    }


def top_risky_devices(db: Session):

    devices = (
        db.query(
            DeviceFingerprint.device_hash,
            func.count(DeviceFingerprint.id).label("usage")
        )
        .group_by(DeviceFingerprint.device_hash)
        .order_by(func.count(DeviceFingerprint.id).desc())
        .limit(10)
        .all()
    )

    return [
        {"device_hash": d.device_hash, "usage": d.usage}
        for d in devices
    ]


def reputation_leaderboard(db: Session):

    records = (
        db.query(Reputation)
        .order_by(Reputation.reputation_score.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "reputation_score": r.reputation_score
        }
        for r in records
    ]


def global_risk_entities(db: Session):

    records = (
        db.query(GlobalFraudSignal)
        .order_by(GlobalFraudSignal.global_risk_score.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "risk_score": r.global_risk_score,
            "merchant_count": r.merchant_count
        }
        for r in records
    ]