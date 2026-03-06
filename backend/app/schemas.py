from pydantic import BaseModel
from typing import Optional


class TransactionSchema(BaseModel):
    merchant_id: Optional[str]
    customer: Optional[str]
    amount: Optional[int]
    currency: Optional[str]
    status: Optional[str]


class DisputeSchema(BaseModel):
    charge: Optional[str]
    reason: Optional[str]
    amount: Optional[int]
    status: Optional[str]


class StripeEventData(BaseModel):
    object: dict


class StripeEvent(BaseModel):
    type: str
    data: StripeEventData
