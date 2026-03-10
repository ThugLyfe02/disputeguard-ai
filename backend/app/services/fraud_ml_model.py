from sklearn.linear_model import LogisticRegression
import numpy as np


class FraudMLModel:

    FEATURE_KEYS = [
        "amount",
        "rule_score",
        "device_risk_score",
        "reputation_score",
        "cluster_risk_score",
    ]

    def __init__(self):
        self.model = LogisticRegression()
        self._trained = False

    def train(self, dataset):

        X = []
        y = []

        for row in dataset:
            X.append([row.get(k, 0) for k in self.FEATURE_KEYS])
            y.append(row["label"])

        X = np.array(X)
        y = np.array(y)

        if len(X) > 0 and len(set(y)) > 1:
            self.model.fit(X, y)
            self._trained = True

    def predict(self, features: dict):

        if not self._trained:
            return 0.5

        X = np.array([[features.get(k, 0) for k in self.FEATURE_KEYS]])

        try:
            probability = self.model.predict_proba(X)[0][1]
            return round(float(probability), 3)
        except Exception:
            return 0.5
