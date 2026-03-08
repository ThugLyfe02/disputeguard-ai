from fastapi import APIRouter

from app.services.behavioral_biometrics import detect_behavior_risk

router = APIRouter()


@router.post("/fraud/behavioral-risk")
def behavioral_risk(session: dict):

    result = detect_behavior_risk(session)

    return result