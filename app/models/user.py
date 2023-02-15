from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from pytz import timezone


class User(BaseModel):
    username: str
    email: str
    password: str
    activation_token: str = None
    is_active: bool = False
    created_at: datetime = datetime.now(timezone("UTC"))
    activated_at: datetime = None

    class Config:
        orm_mode = True


class UserIn(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool


class UserOut(BaseModel):
    username: str
    email: str