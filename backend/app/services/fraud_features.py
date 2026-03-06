def extract_features(transaction, signals):

    return {
        "amount": transaction.amount,
        "signal_count": len(signals),
        "ip_mismatch": any(s.signal_type == "ip_mismatch" for s in signals),
        "high_amount": any(s.signal_type == "high_amount" for s in signals)
    }
