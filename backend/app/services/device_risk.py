from sqlalchemy.orm import Session
from app.models.device_fingerprint import DeviceFingerprint


def detect_device_risk(db: Session, device_hash: str):

    usage_count = db.query(DeviceFingerprint).filter(
        DeviceFingerprint.device_hash == device_hash
    ).count()

    return {
        "device_hash": device_hash,
        "usage_count": usage_count,
        "risk_level": (
            "high" if usage_count > 5
            else "medium" if usage_count > 2
            else "low"
        )
    }
