from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.dashboard_analytics import (
    fraud_overview,
    top_risky_devices,
    reputation_leaderboard,
    global_risk_entities
)

router = APIRouter()


@router.get("/fraud/dashboard/overview")
def overview(db: Session = Depends(get_db)):

    return fraud_overview(db)


@router.get("/fraud/dashboard/top-devices")
def risky_devices(db: Session = Depends(get_db)):

    return top_risky_devices(db)


@router.get("/fraud/dashboard/reputation")
def reputation_board(db: Session = Depends(get_db)):

    return reputation_leaderboard(db)


@router.get("/fraud/dashboard/global-risk")
def global_risk(db: Session = Depends(get_db)):

    return global_risk_entities(db)