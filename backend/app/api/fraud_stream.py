from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

from app.services.fraud_stream import fraud_stream


router = APIRouter()


@router.get("/fraud/stream")
async def fraud_event_stream():
    """
    Real-time fraud intelligence stream.

    This endpoint allows dashboards and monitoring systems
    to subscribe to fraud analysis events in real time.
    """

    async def event_generator():
        async for event in fraud_stream.subscribe():
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )