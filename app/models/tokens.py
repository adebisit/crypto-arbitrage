from pydantic import BaseModel
from bson import ObjectId


class Token(BaseModel):
    user_id: ObjectId
    amount: float
    locked: float = 0.00
    