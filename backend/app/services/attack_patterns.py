def detect_card_testing(transactions):

    small_transactions = [
        t for t in transactions if t.get("amount", 0) < 5
    ]

    return len(small_transactions) > 20


def detect_device_farm(device_usage):

    return device_usage > 50


def detect_account_takeover(login_failures):

    return login_failures > 10