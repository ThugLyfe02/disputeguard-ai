from fastapi import APIRouter
from app.services.billing_service import billing_service

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout")
def create_checkout(payload: dict):

    merchant_id = payload.get("merchant_id")

    url = billing_service.create_checkout_session(merchant_id)

    return {"checkout_url": url}