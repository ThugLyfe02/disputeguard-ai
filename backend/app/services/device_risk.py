from sqlalchemy.orm import Session
from app.models.device_fingerprint import DeviceFingerprint
from app.models.dispute import Dispute
from app.models.transaction import Transaction


def detect_device_risk(db: Session, device_hash: str, merchant_id: str | None = None):
    """
    Evaluate fraud risk for a device fingerprint.

    Signals considered:
    - total device usage
    - merchant-specific usage
    - historical disputes linked to the device
    """

    # Total device usage across all merchants
    total_usage = (
        db.query(DeviceFingerprint)
        .filter(DeviceFingerprint.device_hash == device_hash)
        .count()
    )

    # Usage within the same merchant (important for tenant-safe scoring)
    merchant_usage = 0
    if merchant_id:
        merchant_usage = (
            db.query(DeviceFingerprint)
            .filter(
                DeviceFingerprint.device_hash == device_hash,
                DeviceFingerprint.merchant_id == merchant_id
            )
            .count()
        )

    # Transactions associated with this device
    transactions = (
        db.query(Transaction)
        .filter(Transaction.device_hash == device_hash)
        .all()
    )

    transaction_ids = [tx.id for tx in transactions]

    # Disputes tied to those transactions
    dispute_count = 0
    if transaction_ids:
        dispute_count = (
            db.query(Dispute)
            .filter(Dispute.transaction_id.in_(transaction_ids))
            .count()
        )

    transaction_count = len(transactions)

    dispute_ratio = (
        dispute_count / transaction_count
        if transaction_count > 0 else 0
    )

    # Risk score calculation
    usage_score = min(total_usage / 10, 1)
    dispute_score = min(dispute_ratio * 2, 1)

    risk_score = min((usage_score * 0.4) + (dispute_score * 0.6), 1)

    # Risk classification
    if risk_score > 0.75:
        risk_level = "high"
    elif risk_score > 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "device_hash": device_hash,
        "total_usage": total_usage,
        "merchant_usage": merchant_usage,
        "transaction_count": transaction_count,
        "dispute_count": dispute_count,
        "dispute_ratio": round(dispute_ratio, 3),
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level
    }