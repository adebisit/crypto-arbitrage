from pydantic import BaseModel
from bson import ObjectId


class Token(BaseModel):
    username: str
    amount: float
    locked: float = 0.00
    