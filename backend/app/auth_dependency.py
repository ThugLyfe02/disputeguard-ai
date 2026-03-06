from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt

SECRET_KEY = "disputeguard-secret"
ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_merchant(token=Depends(security)):

    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        merchant_id = payload.get("merchant_id")
        return merchant_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
