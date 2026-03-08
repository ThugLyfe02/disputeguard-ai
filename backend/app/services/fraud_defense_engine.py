from app.services.fraud_actions import (
    block_transaction,
    freeze_device,
    flag_account,
    notify_merchant
)


def autonomous_defense(transaction, investigation_report):
    """
    Execute automated fraud defenses based on investigation results.
    """

    risk_score = investigation_report.get("risk_score", 0)
    actions = []

    if risk_score > 0.85:

        actions.append(
            block_transaction(transaction.get("id"))
        )

        actions.append(
            freeze_device(transaction.get("device_hash"))
        )

        actions.append(
            notify_merchant(
                "High-risk fraud transaction automatically blocked."
            )
        )

    elif risk_score > 0.6:

        actions.append(
            flag_account(transaction.get("customer_id"))
        )

        actions.append(
            notify_merchant(
                "Medium-risk transaction flagged for review."
            )
        )

    else:

        actions.append(
            notify_merchant(
                "Transaction passed fraud checks."
            )
        )

    return {
        "risk_score": risk_score,
        "actions": actions
    }