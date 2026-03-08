from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.control_center import (
    system_overview,
    fraud_heatmap,
    high_risk_entities,
    global_threat_overview
)

router = APIRouter()


@router.get("/fraud/control/overview")
def overview(db: Session = Depends(get_db)):

    return system_overview(db)


@router.get("/fraud/control/heatmap")
def heatmap(db: Session = Depends(get_db)):

    return fraud_heatmap(db)


@router.get("/fraud/control/high-risk")
def high_risk(db: Session = Depends(get_db)):

    return high_risk_entities(db)


@router.get("/fraud/control/global-threats")
def global_threats(db: Session = Depends(get_db)):

    return global_threat_overview(db)