import random


def assign_variant(experiment):

    r = random.random()

    if r < experiment.traffic_split:
        return "A"

    return "B"