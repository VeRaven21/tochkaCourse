from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from pydantic import BaseModel

import sys 
sys.path.append("..")
from database import Instrument, User, get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


class DepositRequest(BaseModel):
    user_id: int
    ticker: str
    amount: float


@router.delete("/user/{user_id}")
def delete_user(user_id: str, authorization: str):
    """Delete a user by id

    Args:
        user_id (int): Id of the user to delete
        authorization (str): Admin authorization token

    Raises:
        HTTPException: Raises 422 if the user is not an admin
        HTTPException: Raises 422 if the user is not found

    Returns:
        str: Success message
    """
    db = next(get_db())
    # Check if the user is an admin
    stmt = select(User).where(User.api_key == authorization).where(User.role == 'ADMIN')
    user = db.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(422, detail="User is not an admin")
    
    stmt = select(User).where(User.id == int(user_id))
    user = db.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(422, detail="User not found")
    
    db.delete(user)
    db.commit()
    db.close()

    return {
        "id": f"{user.id}",
        "name": user.name,
        "role": user.role,
        "api_key": user.api_key,
    }


# !WIP Do not use yet
@router.post("balance/deposit")
def deposit_balance(request: DepositRequest, authorization: str):
    db = next(get_db())
    # Check if the user is an admin
    stmt = select(User).where(User.api_key == authorization).where(User.role == 'ADMIN')
    user = db.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(422, detail="User is not an admin")
    
    stmt = select(User).where(User.id == int(request.user_id))
    user = db.execute(stmt).scalars().first()
    if not user:
        raise HTTPException(422, detail="User not found")
    
    stmt = select(Instrument).where(Instrument.ticker == request.ticker)
    instrument = db.execute(stmt).scalars().first()
    if not instrument:
        raise HTTPException(422, detail="Ticker not found")
    
    if request.amount <= 0:
        raise HTTPException(422, detail="Amount must be greater than 0")
    
    # Update the user's balance
    user.balance += request.amount
    db.commit()
    db.close()
