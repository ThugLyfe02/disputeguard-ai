from sqlalchemy.orm import Session
from app.models.dispute_response import DisputeResponse


def store_dispute_response(db: Session, dispute_id: str, response_text: str):

    response = DisputeResponse(
        dispute_id=dispute_id,
        response_text=response_text
    )

    db.add(response)
    db.commit()
    db.refresh(response)

    return response
