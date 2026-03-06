from sqlalchemy.orm import Session
from app.models.dispute import Dispute
from app.services.evidence_generator import generate_evidence


def create_dispute(db: Session, stripe_event: dict):

    data = stripe_event.get("data", {}).get("object", {})

    dispute = Dispute(
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
        {"id": dispute.transaction_id, "amount": dispute.amount}
    )

    return {
        "dispute_id": dispute.id,
        "evidence": evidence
    }
