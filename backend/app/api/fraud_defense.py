from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_investigator import investigate_transaction
from app.services.fraud_defense_engine import autonomous_defense

router = APIRouter()


@router.post("/fraud/defend")
def defend(data: dict, db: Session = Depends(get_db)):

    transaction = data.get("transaction")
    device_hash = data.get("device_hash")

    investigation = investigate_transaction(
        db,
        transaction,
        device_hash
    )

    defense = autonomous_defense(
        transaction,
        investigation
    )

    return {
        "investigation": investigation,
        "defense_actions": defense
    }