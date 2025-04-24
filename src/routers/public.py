from time import timezone
from webbrowser import get
from fastapi import APIRouter
from datetime import datetime, timezone
import secrets

import sys

sys.path.append("..")
from database import Sessionlocal, User
from models import User as UserModel

router = APIRouter(
    prefix = "/public",
    tags = ["public"]
)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(username: str):
    token = secrets.token_urlsafe(16)

    user = User(
        name=username,
        role='USER',
        balance=0.0,
        balance_lock=0.0,
        regdate=datetime.now(timezone.utc),
        api_key=token
    )

    db = next(get_db())
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "api_key": user.api_key,
    }

