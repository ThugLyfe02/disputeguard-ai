import logging
from datetime import datetime

from app.services.feature_store import get_training_data
from app.services.fraud_ml_model import FraudMLModel

logger = logging.getLogger(__name__)


"""
Adaptive Fraud Model Training Engine

Responsibilities:
• Build training datasets from Feature Store
• Train ML models for fraud prediction
• Version models
• Enable continuous model improvement

This simulates the model lifecycle used in real fraud platforms.
"""


class ModelTrainingService:

    def __init__(self):
        self.model = FraudMLModel()

    def train(self, db):
        """
        Train fraud prediction model using historical fraud features.
        """

        logger.info("Building training dataset")

        dataset = get_training_data(db)

        if len(dataset) < 10:
            logger.warning("Not enough data to train model")

            return {
                "status": "skipped",
                "reason": "not enough training data"
            }

        logger.info(f"Training fraud model with {len(dataset)} samples")

        self.model.train(dataset)

        return {
            "status": "model_trained",
            "samples": len(dataset),
            "trained_at": datetime.utcnow().isoformat()
        }

    def predict(self, amount, signal_count):
        """
        Predict chargeback probability.
        """

        probability = self.model.predict(amount, signal_count)

        return {
            "chargeback_probability": probability,
            "risk_level": (
                "high" if probability > 0.8
                else "medium" if probability > 0.5
                else "low"
            )
        }