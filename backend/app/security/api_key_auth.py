from fastapi import Header, HTTPException

# In production this would come from DB
API_KEYS = {
    "merchant_demo_key": {
        "merchant_id": "demo_merchant",
        "webhook_url": None
    }
}

def authenticate_api_key(x_api_key: str = Header(...)):

    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return API_KEYS[x_api_key]