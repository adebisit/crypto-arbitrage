from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from pytz import timezone


class Token(BaseModel):
    available: int = Field(default=0)
    locked: int = Field(default=0)


class User(BaseModel):
    username: str
    email: str
    password: str
    activation_token: str = None
    token_expires_at: datetime = datetime.utcnow() + timedelta(hours=1)
    is_active: bool = False
    archived: bool = False
    created_at: datetime = datetime.utcnow()
    activated_at: datetime = None
    reset_password_token: str = None
    reset_password_token_expires_at: datetime = None
    token: Token = Field(default=Token())

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


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
    token: Token