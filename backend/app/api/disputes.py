from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.dispute import Dispute
from app.models.evidence_package import EvidencePackage

router = APIRouter()


@router.get("/disputes")
def get_disputes(db: Session = Depends(get_db)):
    disputes = db.query(Dispute).all()
    return disputes


@router.get("/disputes/{dispute_id}/evidence")
def get_dispute_evidence(dispute_id: int, db: Session = Depends(get_db)):

    evidence = db.query(EvidencePackage).filter(
        EvidencePackage.dispute_id == dispute_id
    ).first()

    if not evidence:
        return {"message": "No evidence found for this dispute"}

    return evidence
