from app.services.attack_patterns import (
    detect_card_testing,
    detect_device_farm,
    detect_account_takeover
)


def detect_attack(transactions, device_usage, login_failures):

    alerts = []

    if detect_card_testing(transactions):

        alerts.append({
            "attack": "card_testing",
            "severity": "high"
        })

    if detect_device_farm(device_usage):

        alerts.append({
            "attack": "device_farm",
            "severity": "high"
        })

    if detect_account_takeover(login_failures):

        alerts.append({
            "attack": "account_takeover",
            "severity": "medium"
        })

    return alerts