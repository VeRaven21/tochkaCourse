from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class User(BaseModel):
    name: str    
    role: Literal["USER", "ADMIN"]
    balance: float = 0.0
    balance_lock: float = 0.0
    regdate: datetime = datetime.now()
    api_key: str

