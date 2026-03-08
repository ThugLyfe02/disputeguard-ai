from app.services.experiment_engine import assign_variant


def route_experiment(experiment, transaction):

    variant = assign_variant(experiment)

    return {
        "experiment": experiment.name,
        "variant": variant,
        "transaction_id": transaction.get("id")
    }