from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class User(BaseModel):
    name: str    
    role: Literal["USER", "ADMIN"]
    regdate: datetime
    api_key: str
