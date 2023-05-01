from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from pytz import timezone


class User(BaseModel):
    # id: str
    username: str
    email: str
    password: str
    activation_token: str = None
    token_expires_at: datetime = datetime.utcnow() + timedelta(hours=1)
    is_active: bool = False
    created_at: datetime = datetime.utcnow()
    activated_at: datetime = None

    class Config:
        orm_mode = True


class UserLogIn(BaseModel):
    email: str
    password: str


class UserSignUp(BaseModel):
    username: str
    email: str
    password: str


class UserIn(BaseModel):
    username: str
    email: str
    password: str
    is_active: bool


class UserOut(BaseModel):
    username: str
    email: str