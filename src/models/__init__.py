from pydantic import BaseModel
from typing import Literal

class User(BaseModel):
    id: int
    name: str    
    role: Literal["USER", "ADMIN"]
    api_key: str
    
    class Config:
        orm_mode = True