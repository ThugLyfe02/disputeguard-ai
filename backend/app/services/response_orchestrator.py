from app.services.fraud_actions import (
    block_transaction,
    freeze_device,
    flag_account
)


def orchestrate_response(incident):

    actions = []

    if incident.severity == "high":

        actions.append(
            freeze_device(incident.entity_id)
        )

    if incident.severity == "critical":

        actions.append(
            block_transaction(incident.entity_id)
        )

    if incident.severity == "medium":

        actions.append(
            flag_account(incident.entity_id)
        )

    return actions