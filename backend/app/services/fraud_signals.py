def calculate_risk_score(transaction):
    risk_score = 0

    # Example signals
    if transaction.get("amount", 0) > 1000:
        risk_score += 20

    if transaction.get("ip_country") != transaction.get("billing_country"):
        risk_score += 30

    return risk_score
