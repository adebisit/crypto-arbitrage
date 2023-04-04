from typing import List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from pytz import timezone
from .user import User


class ScanType(str, Enum):
    simple = 'simple'
    two_point = "two_point"
    intercontinental = "InterContinental"


class Scan(BaseModel):
    id: str = Field(default=None, alias="_id") 
    user_id: str = None
    type: ScanType
    exchangeA: str
    exhangeB: str
    coin: str
    coinB: str = None
    startdate: datetime = datetime.now(timezone("UTC"))
    enddate: datetime = None
    intervals: str = None
    active: bool = False
    timestamp: datetime = datetime.now(timezone("UTC"))
    
    class Config:
        orm_mode = True


class ScanUpdate(BaseModel):
    # startdate: datetime = datetime.now(timezone("UTC"))
    active: bool = False

