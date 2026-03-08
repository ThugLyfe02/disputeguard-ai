from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_model_training import train_fraud_model
from app.services.fraud_model_deployment import deploy_model

router = APIRouter()


@router.post("/fraud/models/train")
def train_model(db: Session = Depends(get_db)):

    return train_fraud_model(db)


@router.post("/fraud/models/deploy/{model_name}")
def deploy(model_name: str):

    return deploy_model(model_name)