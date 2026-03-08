from app.models.fraud_policy import FraudPolicy
from app.services.policy_evaluator import evaluate_condition


def evaluate_policies(db, fraud_signals):
    """
    Evaluate dynamic fraud policies stored in the database.

    Each policy contains:
        signal      -> fraud signal name
        operator    -> comparison operator
        threshold   -> numeric threshold
        action      -> BLOCK / REVIEW / ALERT

    Example policy:

        IF ml_prediction > 0.85
        THEN BLOCK

    This engine evaluates policies sequentially and returns
    the triggered actions.
    """

    policies = db.query(FraudPolicy).order_by(FraudPolicy.priority.desc()).all()

    triggered_actions = []

    for policy in policies:

        value = fraud_signals.get(policy.signal)

        if value is None:
            continue

        if evaluate_condition(value, policy.operator, policy.threshold):

            triggered_actions.append({
                "policy": policy.name,
                "signal": policy.signal,
                "value": value,
                "operator": policy.operator,
                "threshold": policy.threshold,
                "action": policy.action
            })

    # ---------------------------------------------------
    # Resolve final decision
    # ---------------------------------------------------

    decision = "APPROVE"

    for action in triggered_actions:

        if action["action"] == "BLOCK":
            decision = "BLOCK"
            break

        if action["action"] == "REVIEW":
            decision = "REVIEW"

    return {
        "decision": decision,
        "triggered_policies": triggered_actions
    }