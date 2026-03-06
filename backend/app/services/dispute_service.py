from sqlalchemy.orm import Session

from app.models.dispute import Dispute
from app.services.evidence_generator import generate_evidence
from app.services.evidence_service import store_evidence
from app.services.ai_dispute_response import generate_dispute_response
from app.services.dispute_response_service import store_dispute_response


def create_dispute(db: Session, stripe_event: dict, merchant_id: int):

    data = stripe_event.get("data", {}).get("object", {})

    dispute = Dispute(
        merchant_id=merchant_id,
        transaction_id=data.get("charge"),
        reason=data.get("reason", "unknown"),
        amount=data.get("amount", 0) / 100 if data.get("amount") else 0,
        status=data.get("status", "open"),
    )

    db.add(dispute)
    db.commit()
    db.refresh(dispute)

    evidence = generate_evidence(
        {"reason": dispute.reason},
        {"transaction_id": dispute.transaction_id, "amount": dispute.amount}
    )

    store_evidence(db, dispute.id, str(evidence))

    ai_response = generate_dispute_response(
        {"reason": dispute.reason},
        {"transaction_id": dispute.transaction_id, "amount": dispute.amount}
    )

    store_dispute_response(db, dispute.id, ai_response)

    return {
        "dispute_id": dispute.id,
        "evidence": evidence,
        "ai_response": ai_response
    }
