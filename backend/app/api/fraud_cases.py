from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.services.case_management import (
    create_case,
    assign_case,
    add_case_note,
    resolve_case
)

from pydantic import BaseModel


router = APIRouter()


# ================================
# Request Schemas
# ================================

class CreateCaseRequest(BaseModel):
    transaction_id: str
    merchant_id: str
    risk_score: float


class AssignCaseRequest(BaseModel):
    case_id: int
    analyst: str


class CaseNoteRequest(BaseModel):
    case_id: int
    analyst: str
    note: str


class ResolveCaseRequest(BaseModel):
    case_id: int
    outcome: str


# ================================
# Fraud Case Creation
# ================================

@router.post("/fraud/cases/create")
def open_case(
    data: CreateCaseRequest,
    db: Session = Depends(get_db)
):
    """
    Open a new fraud investigation case.

    Triggered when fraud signals exceed thresholds.
    """

    return create_case(
        db,
        data.transaction_id,
        data.merchant_id,
        data.risk_score
    )


# ================================
# Case Assignment
# ================================

@router.post("/fraud/cases/assign")
def assign(
    data: AssignCaseRequest,
    db: Session = Depends(get_db)
):
    """
    Assign a case to an analyst.
    """

    result = assign_case(
        db,
        data.case_id,
        data.analyst
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    return result


# ================================
# Add Investigation Note
# ================================

@router.post("/fraud/cases/note")
def note(
    data: CaseNoteRequest,
    db: Session = Depends(get_db)
):
    """
    Add investigation note to a case.
    """

    return add_case_note(
        db,
        data.case_id,
        data.analyst,
        data.note
    )


# ================================
# Resolve Case
# ================================

@router.post("/fraud/cases/resolve")
def resolve(
    data: ResolveCaseRequest,
    db: Session = Depends(get_db)
):
    """
    Resolve a fraud case with final outcome.

    Example outcomes:
    - fraud_confirmed
    - false_positive
    - refunded
    """

    return resolve_case(
        db,
        data.case_id,
        data.outcome
    )


# ================================
# Investigation Health Check
# ================================

@router.get("/fraud/cases/health")
def fraud_case_system_health():
    """
    Quick endpoint to verify fraud case system is operational.
    """

    return {
        "status": "fraud_case_system_operational"
    }