from fastapi import APIRouter

from app.services.attack_detection import detect_attack

router = APIRouter()


@router.post("/fraud/attack-detection")
def attack_detection(data: dict):

    transactions = data.get("transactions", [])

    device_usage = data.get("device_usage", 0)

    login_failures = data.get("login_failures", 0)

    return detect_attack(
        transactions,
        device_usage,
        login_failures
    )