from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db
from app.auth_dependency import get_current_merchant

from app.models.dispute import Dispute

router = APIRouter()


@router.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    merchant_id: int = Depends(get_current_merchant)
):

    total_disputes = db.query(Dispute).filter(
        Dispute.merchant_id == merchant_id
    ).count()

    open_disputes = db.query(Dispute).filter(
        Dispute.merchant_id == merchant_id,
        Dispute.status == "open"
    ).count()

    total_amount = db.query(
        func.sum(Dispute.amount)
    ).filter(
        Dispute.merchant_id == merchant_id
    ).scalar()

    return {
        "total_disputes": total_disputes,
        "open_disputes": open_disputes,
        "total_disputed_amount": total_amount or 0
    }
