import hashlib


def generate_device_hash(ip, user_agent):

    raw = f"{ip}-{user_agent}"

    return hashlib.sha256(raw.encode()).hexdigest()
