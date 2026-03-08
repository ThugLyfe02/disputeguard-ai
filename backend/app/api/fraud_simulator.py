from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.fraud_simulator import run_simulation

router = APIRouter()


@router.post("/fraud/simulate/{scenario}")
def simulate_fraud(scenario: str, db: Session = Depends(get_db)):

    return run_simulation(db, scenario)