from typing import List
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from pytz import timezone
from .user import User


class ScanType(str, Enum):
    simple = 'simple'
    two_point = "two_point"
    intercontinental = "InterContinental"


class Scan(BaseModel):
    id: str
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

