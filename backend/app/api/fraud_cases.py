from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.case_management import (
    create_case,
    assign_case,
    add_case_note,
    resolve_case
)

router = APIRouter()


@router.post("/fraud/cases/create")
def open_case(data: dict, db: Session = Depends(get_db)):

    return create_case(
        db,
        data["transaction_id"],
        data["merchant_id"],
        data["risk_score"]
    )


@router.post("/fraud/cases/assign")
def assign(data: dict, db: Session = Depends(get_db)):

    return assign_case(
        db,
        data["case_id"],
        data["analyst"]
    )


@router.post("/fraud/cases/note")
def note(data: dict, db: Session = Depends(get_db)):

    return add_case_note(
        db,
        data["case_id"],
        data["analyst"],
        data["note"]
    )


@router.post("/fraud/cases/resolve")
def resolve(data: dict, db: Session = Depends(get_db)):

    return resolve_case(
        db,
        data["case_id"],
        data["outcome"]
    )