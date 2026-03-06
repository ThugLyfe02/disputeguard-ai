from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.auth_dependency import get_current_merchant
from app.services.merchant_behavior import analyze_merchant_behavior

router = APIRouter()


@router.get("/behavior/profile")
def get_behavior_profile(
    db: Session = Depends(get_db),
    merchant_id: int = Depends(get_current_merchant)
):

    profile = analyze_merchant_behavior(db, merchant_id)

    return profile
