from typing import Optional
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime
from pydantic import Field


class CardAuthorization(BaseModel):
    user_id: ObjectId
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
    user_id: ObjectId
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
