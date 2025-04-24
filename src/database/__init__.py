from datetime import datetime, timezone
from dotenv import load_dotenv
import os

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

load_dotenv()


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
    role = Column(String(5), nullable=False)
    balance = Column(Float, default=0.0)
    balance_lock = Column(Float, default=0.0)
    regdate = Column(DateTime, default=datetime.now(timezone.utc))
    api_key = Column(String(50), unique=True, nullable=False)


Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)

