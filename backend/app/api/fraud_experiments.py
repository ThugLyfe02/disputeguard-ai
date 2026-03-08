from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.fraud_experiment import FraudExperiment

router = APIRouter()


@router.post("/fraud/experiments/create")
def create_experiment(data: dict, db: Session = Depends(get_db)):

    experiment = FraudExperiment(
        name=data["name"],
        experiment_type=data["experiment_type"],
        variant_a=data["variant_a"],
        variant_b=data["variant_b"],
        traffic_split=data["traffic_split"]
    )

    db.add(experiment)
    db.commit()

    return experiment


@router.get("/fraud/experiments")
def list_experiments(db: Session = Depends(get_db)):

    return db.query(FraudExperiment).all()