from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.global_intelligence import get_global_risk


router = APIRouter()

"""
Global Fraud Intelligence API

Provides network-level fraud intelligence signals
aggregated across merchants.

Entities supported:
- device_hash
- email
- ip
- customer_id
"""


@router.get("/fraud/global/{entity_type}/{entity_id}")
def global_risk(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    """
    Query global fraud risk for a given entity.

    Example:
        /fraud/global/device_hash/abc123
        /fraud/global/email/test@email.com
    """

    result = get_global_risk(db, entity_type, entity_id)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "global_analysis": result
    }