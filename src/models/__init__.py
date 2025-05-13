from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class User(BaseModel):
    name: str    
    role: Literal["USER", "ADMIN"]
    balance: float
    balance_lock: float
    regdate: datetime
    api_key: str
