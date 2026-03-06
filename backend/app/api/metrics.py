from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db
from app.models.dispute import Dispute

router = APIRouter()


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):

    total_disputes = db.query(Dispute).count()

    open_disputes = db.query(Dispute).filter(
        Dispute.status == "open"
    ).count()

    total_amount = db.query(func.sum(Dispute.amount)).scalar()

    return {
        "total_disputes": total_disputes,
        "open_disputes": open_disputes,
        "total_disputed_amount": total_amount or 0
    }
