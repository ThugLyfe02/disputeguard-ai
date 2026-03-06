from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "disputeguard-secret"
ALGORITHM = "HS256"


def create_access_token(merchant_id: int):

    payload = {
        "merchant_id": merchant_id,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token
