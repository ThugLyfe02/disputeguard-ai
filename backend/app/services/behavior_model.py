class BehaviorMLModel:

    def train(self, dataset):
        pass

    def predict(self, features):

        score = (
            features["typing_score"] +
            features["checkout_score"] +
            (1 - features["mouse_entropy"]) +
            (1 - features["dwell_score"])
        ) / 4

        return score