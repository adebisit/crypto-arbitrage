from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from pydantic import Field


class CardAuthorization(BaseModel):
    username: str
    authorization_code: str
    brand: str
    card_type: str
    card_bin: str
    last4: str
    exp_month: int
    exp_year: int

    class Config:
        arbitrary_types_allowed = True


class Payment(BaseModel):
    username: str
    token_tier: str
    token_pricing: float
    no_tokens: int
    amount: float
    reference_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    status: str = "pending"
    paid_at: datetime = None

    class Config:
        arbitrary_types_allowed = True


class PaymentOut(BaseModel):
    token_tier: str
    token_pricing: float
    no_tokens: int
    amount: float
    timestamp: datetime
    status: str
    paid_at: Optional[datetime]