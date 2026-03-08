from app.services.fraud_pipeline import run_fraud_pipeline
from app.services.fraud_alerts import generate_alert

from app.services.fraud_scenarios import (
    simulate_device_farm,
    simulate_card_testing,
    simulate_fraud_ring
)


def run_simulation(db, scenario_name):

    if scenario_name == "device_farm":
        event = simulate_device_farm()

    elif scenario_name == "card_testing":
        event = simulate_card_testing()

    elif scenario_name == "fraud_ring":
        event = simulate_fraud_ring()

    else:
        return {"error": "unknown scenario"}

    fraud_result = run_fraud_pipeline(
        db,
        event["transaction"],
        event["device_hash"]
    )

    alert = generate_alert(fraud_result)

    return {
        "scenario": event["scenario"],
        "transaction": event["transaction"],
        "fraud_result": fraud_result,
        "alert": alert
    }