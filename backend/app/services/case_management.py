from app.models.fraud_case import FraudCase
from app.models.case_note import CaseNote


def create_case(db, transaction_id, merchant_id, risk_score):

    case = FraudCase(
        transaction_id=transaction_id,
        merchant_id=merchant_id,
        risk_score=risk_score,
        status="open"
    )

    db.add(case)
    db.commit()

    return case


def assign_case(db, case_id, analyst):

    case = db.query(FraudCase).filter(
        FraudCase.id == case_id
    ).first()

    if not case:
        return {"error": "case_not_found"}

    case.assigned_to = analyst

    db.commit()

    return case


def add_case_note(db, case_id, analyst, note):

    entry = CaseNote(
        case_id=case_id,
        analyst=analyst,
        note=note
    )

    db.add(entry)
    db.commit()

    return entry


def resolve_case(db, case_id, outcome):

    case = db.query(FraudCase).filter(
        FraudCase.id == case_id
    ).first()

    if not case:
        return {"error": "case_not_found"}

    case.status = outcome

    db.commit()

    return case