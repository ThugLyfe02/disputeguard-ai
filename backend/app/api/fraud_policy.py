from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.fraud_policy import FraudPolicy

router = APIRouter()


@router.post("/fraud/policies/create")
def create_policy(data: dict, db: Session = Depends(get_db)):

    policy = FraudPolicy(
        name=data["name"],
        signal=data["signal"],
        operator=data["operator"],
        threshold=data["threshold"],
        action=data["action"]
    )

    db.add(policy)
    db.commit()

    return policy


@router.get("/fraud/policies")
def list_policies(db: Session = Depends(get_db)):

    return db.query(FraudPolicy).all()