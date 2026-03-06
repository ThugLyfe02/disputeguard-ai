def generate_evidence(dispute, transaction):
    evidence = {
        "transaction_id": transaction.get("id"),
        "amount": transaction.get("amount"),
        "customer_id": transaction.get("customer_id"),
        "reason": dispute.get("reason"),
        "timeline": [
            "Payment authorized",
            "Order processed",
            "Shipment confirmed",
            "Delivery completed"
        ],
        "fraud_indicators": [],
    }

    return evidence
