from fastapi import APIRouter
from app.services.graph_signal_cache import graph_signal_cache

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/device/{device_id}")
def device_risk(device_id: str):

    node = f"device_{device_id}"

    return graph_signal_cache.get_signals(node)