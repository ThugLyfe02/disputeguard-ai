from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.device_risk import detect_device_risk

router = APIRouter()


@router.get("/devices/{device_hash}/risk")
def get_device_risk(device_hash: str, db: Session = Depends(get_db)):

    return detect_device_risk(db, device_hash)
