from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.customer_risk import calculate_customer_risk

router = APIRouter()


@router.get("/customers/{customer_id}/risk")
def get_customer_risk(customer_id: str, db: Session = Depends(get_db)):

    risk = calculate_customer_risk(db, customer_id)

    return risk
