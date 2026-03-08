from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.device_fingerprint import DeviceFingerprint

def detect_cross_merchant_activity(db: Session, device_hash: str):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.device_hash == device_hash)
        .all()
    )

    merchants = set(t.merchant_id for t in transactions)

    return {
        "device_hash": device_hash,
        "merchant_count": len(merchants),
        "merchants": list(merchants),
        "suspicious": len(merchants) > 1
    }