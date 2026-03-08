def evaluate_condition(value, operator, threshold):

    if operator == ">":
        return value > threshold

    if operator == "<":
        return value < threshold

    if operator == ">=":
        return value >= threshold

    if operator == "<=":
        return value <= threshold

    return False