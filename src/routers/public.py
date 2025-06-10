from time import timezone
from fastapi import APIRouter,  HTTPException
from datetime import datetime, timezone
import secrets

import sys

sys.path.append("..")
from database import Instrument, User, get_db, Balance
from models import User as UserModel

from sqlalchemy import select

router = APIRouter(
    prefix = "/public",
    tags = ["public"]
)



def verify_user_key(api_key: str)-> bool:
    """Chek if the user key is valid

    Args:
        api_key (str): Api key to check

    Returns:
        Bool: Returns True if the key is valid, False otherwise
    """
    db =  next(get_db())
    stmt = select(User).where(User.api_key == api_key)
    user = db.execute(stmt).scalars().first()

    db.close()

    if user:
        return True
    return False



@router.post("/register")
def register(username: str):
    """Register a new user

    Args:
        username str: Username of the new user

    Raises:
        HTTPException: Raises 422 if given username isn't string
        HTTPException: Raises 409 if the username is already taken

    Returns:
        str: Api key of the new user
    """
    db = next(get_db())

    stmt = select(User).where(User.name == username)
    user = db.execute(stmt).scalars().first()

    if user:
        db.close()
        raise HTTPException(status_code=409, detail="Username already taken")

    token: str = secrets.token_urlsafe(16) 

    # Check if the token is unique
    stmt = select(User).where(User.api_key == token)
    user = db.execute(stmt).scalars().first()
    while user:
        token = secrets.token_urlsafe(16)
        stmt = select(User).where(User.api_key == token)
        user = db.execute(stmt).scalars().first()

    user = User(
        name=username,
        role='USER',
        regdate=datetime.now(timezone.utc),
        api_key=token
    )
    # Validate the user model
    try:
        pydantic_model = UserModel.model_validate(user)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=422, detail=str(e))

    balance = Balance(
        user_id=user.id,
        timestamp=datetime.now(timezone.utc),
        ticker="RUB", # RUB is base currency
        qty=0,
        lock_qty=0
    )

    db.add(user)
    db.add(balance)
    db.commit()
    db.refresh(user)
    db.close()

    return {
        "id": f"{user.id}",
        "name": user.name,
        "role": user.role,
        "api_key": user.api_key,
    }


@router.get("/instrument")
def get_instrumenst():
    """Get all instruments

    Returns:
        Array[Dict]: List of instruments
    """
    db = next(get_db())

    instruments = db.query(Instrument).all()
    db.close()

    return [{"name": el.name, "ticker": el.ticker} for el in instruments]


@router.get("/admins")
def get_admins():
    """
    Temporary solution to get list of admin api keys
    Get all admins


    TODO: Remove this endpoint in production

    Returns:
        Array[Dict]: List of admins
    """
    db = next(get_db())

    stmt = select(User).where(User.role == 'ADMIN')
    admins = db.execute(stmt).scalars().all()
    db.close()

    return [{"id": el.id, "name": el.name, "role": el.role, "api_key": el.api_key} for el in admins]