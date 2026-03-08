"""
merchant_auth.py

Simple merchant authentication layer.

Protects fraud scoring APIs and enables multi-tenant SaaS access.
"""

from fastapi import Header, HTTPException

# Temporary in-memory merchant store
# Later this becomes a database table
MERCHANTS = {
    "demo_key_123": {
        "merchant_id": "merchant_demo",
        "subscription_active": True
    }
}


def authenticate_merchant(x_api_key: str = Header(...)):

    merchant = MERCHANTS.get(x_api_key)

    if not merchant:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not merchant.get("subscription_active"):
        raise HTTPException(status_code=403, detail="Subscription inactive")

    return merchant