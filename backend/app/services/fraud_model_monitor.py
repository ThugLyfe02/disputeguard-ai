def evaluate_model_performance(predictions):

    correct = 0

    for p in predictions:

        predicted = p["prediction"]
        actual = p["actual"]

        if round(predicted) == actual:
            correct += 1

    accuracy = correct / len(predictions) if predictions else 0

    return {
        "accuracy": round(accuracy, 3),
        "samples": len(predictions)
    }