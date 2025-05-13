from datetime import datetime, timezone
from tabnanny import verbose
from dotenv import load_dotenv
import os

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    ForeignKey, Enum
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


# Load database credentials 
load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PSWD")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")

url = f'postgresql+psycopg2://{user}:{password}@{db_host}:{port}/{db_name}'

engine = create_engine(
    url,
    echo=True,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800
)

Base = declarative_base()

RolesEnum = Enum('USER', 'ADMIN', name='roles')
DirectionsEnum = Enum('BUY', 'SELL', name='directions')
OrderStatusEnum = Enum('NEW', 'EXECUTED', 'PARTIALLY_EXECUTED', name='order_status')

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(RolesEnum, nullable=False)
    balance = Column(Float, default=0.0)
    balance_lock = Column(Float, default=0.0)
    regdate = Column(DateTime, default=datetime.now(timezone.utc))
    api_key = Column(String, unique=True, nullable=False)

class Instrument(Base):
    __tablename__ = 'instruments'

    ticker = Column(String, primary_key=True)
    name = Column(String, nullable=False)

class LimitOrder(Base):
    __tablename__ = 'limit_orders'

    id = Column(Integer, primary_key=True)
    status = Column(OrderStatusEnum, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    direction = Column(DirectionsEnum, nullable=False)
    ticker = Column(String, ForeignKey('instruments.ticker'), nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    qty_filled = Column(Integer, default=0)

class MarketOrder(Base):
    __tablename__ = 'market_orders'

    id = Column(Integer, primary_key=True)
    status = Column(OrderStatusEnum, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    direction = Column(DirectionsEnum, nullable=False)
    ticker = Column(String, ForeignKey('instruments.ticker'), nullable=False)
    qty = Column(Integer, nullable=False)
    qty_filled = Column(Integer, default=0)

# Create all tables
Base.metadata.create_all(engine)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()