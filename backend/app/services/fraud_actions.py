def block_transaction(transaction_id):
    """
    Simulated transaction blocking.
    In production this could call a payment gateway API.
    """
    return {
        "action": "block_transaction",
        "transaction_id": transaction_id,
        "status": "blocked"
    }


def freeze_device(device_hash):
    """
    Mark a device as temporarily frozen.
    """
    return {
        "action": "freeze_device",
        "device_hash": device_hash,
        "status": "frozen"
    }


def flag_account(customer_id):
    """
    Flag a customer account for manual investigation.
    """
    return {
        "action": "flag_account",
        "customer_id": customer_id,
        "status": "flagged"
    }


def notify_merchant(message):
    """
    Send a notification event to the merchant.
    """
    return {
        "action": "notify_merchant",
        "message": message
    }