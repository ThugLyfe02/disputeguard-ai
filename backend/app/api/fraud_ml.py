from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_ml_prediction import train_model

router = APIRouter()


@router.post("/fraud/train-model")
def train_fraud_model(db: Session = Depends(get_db)):

    return train_model(db)
