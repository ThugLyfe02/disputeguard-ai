from sqlalchemy.orm import Session
from app.models.evidence_package import EvidencePackage


def store_evidence(db: Session, dispute_id: str, evidence_summary: str):

    evidence = EvidencePackage(
        dispute_id=dispute_id,
        evidence_summary=evidence_summary
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence
