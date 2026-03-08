from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.event_stream_processor import ingest_event
from app.services.fraud_worker import process_event

router = APIRouter()


@router.post("/fraud/stream")
def stream_fraud_event(data: dict):

    transaction = data.get("transaction")

    device_hash = data.get("device_hash")

    return ingest_event(transaction, device_hash)


@router.post("/fraud/process-next")
def process_next_event(db: Session = Depends(get_db)):

    return process_event(db)