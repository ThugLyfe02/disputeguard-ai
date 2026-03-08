from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.global_intelligence import (
    check_global_device_risk,
    check_global_email_risk
)

router = APIRouter()


"""
Global Fraud Intelligence API

Provides network-level fraud detection signals across merchants.
"""


@router.get("/fraud/global/device/{device_hash}")
def global_device_risk(device_hash: str, db: Session = Depends(get_db)):
    """
    Check if a device fingerprint has been used across merchants
    and calculate global fraud risk.
    """

    result = check_global_device_risk(db, device_hash)

    return {
        "entity_type": "device",
        "device_hash": device_hash,
        "global_analysis": result
    }


@router.get("/fraud/global/email/{email}")
def global_email_risk(email: str, db: Session = Depends(get_db)):
    """
    Evaluate fraud risk of an email across all merchants.
    """

    result = check_global_email_risk(db, email)

    return {
        "entity_type": "email",
        "email": email,
        "global_analysis": result
    }