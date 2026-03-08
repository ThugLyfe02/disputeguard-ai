"""
merchant_dashboard.py

Aggregated risk signals for merchant dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.graph_signal_cache import graph_signal_cache

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/merchant/{merchant_id}")
def merchant_risk_summary(merchant_id: str, db: Session = Depends(get_db)):

    merchant_node = f"merchant_{merchant_id}"

    return {
        "merchant_id": merchant_id,
        "cluster_risk": graph_signal_cache.get_cluster_risk(merchant_node),
        "cross_merchant": graph_signal_cache.get_cross_merchant(merchant_node),
        "velocity": graph_signal_cache.get_velocity(merchant_node),
        "cluster_size": graph_signal_cache.get_cluster_size(merchant_node),
    }