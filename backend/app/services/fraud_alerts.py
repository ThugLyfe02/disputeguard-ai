def generate_alert(fraud_result):

    probability = fraud_result["ml_prediction"]["chargeback_probability"]

    if probability > 0.8:
        return {
            "alert": "HIGH_RISK_TRANSACTION",
            "message": "Transaction likely to become a chargeback"
        }

    if probability > 0.5:
        return {
            "alert": "MEDIUM_RISK_TRANSACTION",
            "message": "Transaction shows fraud signals"
        }

    return {"alert": "LOW_RISK"}
