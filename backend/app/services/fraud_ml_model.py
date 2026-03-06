from sklearn.linear_model import LogisticRegression
import numpy as np


class FraudMLModel:

    def __init__(self):
        self.model = LogisticRegression()

    def train(self, dataset):

        X = []
        y = []

        for row in dataset:
            X.append([
                row["amount"],
                row["signal_count"]
            ])
            y.append(row["label"])

        X = np.array(X)
        y = np.array(y)

        if len(X) > 0:
            self.model.fit(X, y)

    def predict(self, amount, signal_count):

        features = np.array([[amount, signal_count]])

        probability = self.model.predict_proba(features)[0][1]

        return round(float(probability), 3)
