from app.services.event_bus import event_bus
from app.services.merchant_webhooks import send_webhook


def handle(event):

    fraud_result = event.get("fraud_result")

    webhook_url = fraud_result.get("merchant_webhook")

    if not webhook_url:
        return

    payload = {
        "event": "fraud_alert",
        "transaction_id": fraud_result["transaction_id"],
        "scores": fraud_result["scores"],
    }

    return send_webhook(webhook_url, payload)


def register():

    event_bus.subscribe(
        "fraud.analysis.completed",
        handle
    )