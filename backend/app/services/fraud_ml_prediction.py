from app.services.fraud_ml_model import FraudMLModel
from app.services.fraud_training_data import build_training_dataset

model = FraudMLModel()


def train_model(db):

    dataset = build_training_dataset(db)

    model.train(dataset)

    return {"status": "model_trained", "samples": len(dataset)}


def predict_chargeback(amount, signal_count):

    probability = model.predict(amount, signal_count)

    return {
        "chargeback_probability": probability
    }
