from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.dispute import Dispute

router = APIRouter()


@router.get("/disputes")
def get_disputes(db: Session = Depends(get_db)):

    disputes = db.query(Dispute).all()

    return disputes
