from app.services.fraud_ml_model import FraudMLModel
from app.services.fraud_training_data import build_training_dataset


# Initialize global model instance
model = FraudMLModel()


def train_model(db):
    """
    Train the fraud ML model using historical transaction data.
    """

    dataset = build_training_dataset(db)

    if not dataset:
        return {
            "status": "no_training_data"
        }

    model.train(dataset)

    return {
        "status": "model_trained",
        "samples": len(dataset)
    }


def predict_chargeback(
    amount: float,
    rule_score: float = 0,
    device_risk_score: float = 0,
    reputation_score: float = 0,
    cluster_risk_score: float = 0
):
    """
    Predict chargeback probability using multiple fraud signals.

    Features used:
    - transaction amount
    - rule-based fraud score
    - device reputation
    - entity reputation
    - fraud graph cluster score
    """

    features = {
        "amount": amount,
        "rule_score": rule_score,
        "device_risk_score": device_risk_score,
        "reputation_score": reputation_score,
        "cluster_risk_score": cluster_risk_score
    }

    probability = model.predict(features)

    # Risk classification
    if probability > 0.8:
        risk_level = "high"
    elif probability > 0.5:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "chargeback_probability": round(probability, 4),
        "risk_level": risk_level,
        "features_used": features
    }