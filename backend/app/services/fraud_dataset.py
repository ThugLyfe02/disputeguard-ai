from app.services.fraud_features import extract_features


def build_dataset(transactions):

    dataset = []

    for tx, signals in transactions:
        features = extract_features(tx, signals)

        dataset.append(features)

    return dataset
