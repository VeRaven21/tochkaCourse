from datetime import datetime, timezone
from dotenv import load_dotenv
import os

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

# Load environment variables
load_dotenv()

# Database configuration
user = os.getenv("DB_USER")
password = os.getenv("DB_PSWD")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

url = f'postgresql+psycopg2://{user}:{password}@localhost:{port}/{db_name}'

engine = create_engine(
    url,
    echo=True,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800
)

Base = declarative_base()

# Models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    balance = Column(Float, default=0.0)
    regdate = Column(DateTime, default=datetime.now(timezone.utc))
    isadmin = Column(Boolean, default=False)

    # Relationships
    created_instruments = relationship("Instrument", back_populates="creator_user", cascade="all, delete-orphan")
    sells = relationship("Sell", back_populates="seller", cascade="all, delete-orphan")
    buys = relationship("Buy", back_populates="buyer", cascade="all, delete-orphan")


class Instrument(Base):
    __tablename__ = 'instrument'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    creationdate = Column(DateTime, default=datetime.now(timezone.utc))
    creator = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    creator_user = relationship("User", back_populates="created_instruments")
    sells = relationship("Sell", back_populates="instrument", cascade="all, delete-orphan")
    buys = relationship("Buy", back_populates="instrument", cascade="all, delete-orphan")


class Sell(Base):
    __tablename__ = 'sells'

    id = Column(Integer, primary_key=True)
    sellerid = Column(Integer, ForeignKey('users.id'), nullable=False)
    instrumentid = Column(Integer, ForeignKey('instrument.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    creationdate = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    seller = relationship("User", back_populates="sells")
    instrument = relationship("Instrument", back_populates="sells")


class Buy(Base):
    __tablename__ = 'buys'

    id = Column(Integer, primary_key=True)
    buyerid = Column(Integer, ForeignKey('users.id'), nullable=False)
    instrumentid = Column(Integer, ForeignKey('instrument.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    creationdate = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    buyer = relationship("User", back_populates="buys")
    instrument = relationship("Instrument", back_populates="buys")



Base.metadata.create_all(engine)

Sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
