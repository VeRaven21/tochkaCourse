import string
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from pydantic import BaseModel

import sys 
sys.path.append("..")
from database import Balance, Instrument, User, get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


class DepositRequest(BaseModel):
    user_id: int
    ticker: str
    amount: float

class instrumentRequest(BaseModel):
    name: string
    ticker: string


def verify_admin_key(api_key: str) -> bool:
    """Check if the user key is valid and the user is an admin

    Args:
        api_key (str): Api key to check

    Returns:
        bool: Returns True if the key is valid and the user is an admin, False otherwise
    """
    db = next(get_db())
    stmt = select(User).where(User.api_key == api_key).where(User.role == 'ADMIN')
    user = db.execute(stmt).scalars().first()
    
    db.close()

    return user is not None

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
    if not verify_admin_key(authorization):
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


@router.post("balance/deposit")
def deposit_balance(request: DepositRequest, authorization: str):
    db = next(get_db())
    # Check if the user is an admin
    if not verify_admin_key(authorization):
        raise HTTPException(422, detail="User is not an admin")
    
    # Check if target user exists
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
    
    stmt = select(Balance).where(Balance.user_id == user.id).where(Balance.ticker == request.ticker)

    # Update the user's balance
    balance = db.execute(stmt).scalars().first()
    balance.qty += request.amount
    
    db.commit()
    db.close()

@router.post("/instrument")
def add_instrument(request: instrumentRequest, authorization: str):
    """Creates a new instrument

    Args:
        request (_type_): _description_
        authorization (_type_): _description_
    """

    db = next(get_db())
    # Check if the user is an admin
    if not verify_admin_key(authorization):
        raise HTTPException(422, detail="User is not an admin")
    
    # Check if the instrument already exists
    stmt = select(Instrument).where(Instrument.ticker == request.ticker)
    instrument = db.execute(stmt).scalars().first()
    if instrument:
        raise HTTPException(422, detail="Instrument already exists")
    
    # Create a new instrument
    instrument = Instrument(
        name=request.name,
        ticker=request.ticker
    )
    db.add(instrument)
    db.commit()
    db.close()

    return { "success": True } 