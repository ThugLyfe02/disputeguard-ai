import random
import uuid


def simulate_device_farm():

    device_hash = f"device_{uuid.uuid4().hex[:8]}"

    return {
        "scenario": "device_farm",
        "transaction": {
            "id": f"tx_{uuid.uuid4().hex[:8]}",
            "customer_id": f"cust_{random.randint(1,100)}",
            "amount": random.randint(50, 500),
        },
        "device_hash": device_hash
    }


def simulate_card_testing():

    return {
        "scenario": "card_testing",
        "transaction": {
            "id": f"tx_{uuid.uuid4().hex[:8]}",
            "customer_id": f"cust_{random.randint(1,50)}",
            "amount": random.randint(1, 5),
        },
        "device_hash": f"device_{uuid.uuid4().hex[:8]}"
    }


def simulate_fraud_ring():

    ring_id = uuid.uuid4().hex[:6]

    return {
        "scenario": "fraud_ring",
        "transaction": {
            "id": f"tx_{uuid.uuid4().hex[:8]}",
            "customer_id": f"ring_user_{ring_id}",
            "amount": random.randint(200, 1000),
        },
        "device_hash": f"ring_device_{ring_id}"
    }