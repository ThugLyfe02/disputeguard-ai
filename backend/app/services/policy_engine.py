from app.models.fraud_policy import FraudPolicy
from app.services.policy_evaluator import evaluate_condition


def evaluate_policies(db, fraud_signals):

    policies = db.query(FraudPolicy).all()

    triggered_actions = []

    for policy in policies:

        value = fraud_signals.get(policy.signal)

        if value is None:
            continue

        if evaluate_condition(value, policy.operator, policy.threshold):

            triggered_actions.append({
                "policy": policy.name,
                "action": policy.action
            })

    return triggered_actions