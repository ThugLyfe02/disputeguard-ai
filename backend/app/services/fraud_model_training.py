from app.services.fraud_training_data import build_training_dataset
from app.services.fraud_ml_model import FraudMLModel
from app.services.fraud_model_registry import register_model


def train_fraud_model(db):

    dataset = build_training_dataset(db)

    if not dataset:
        return {"status": "no_data"}

    model = FraudMLModel()

    model.train(dataset)

    register_model("fraud_model_v1", model)

    return {
        "status": "trained",
        "samples": len(dataset)
    }