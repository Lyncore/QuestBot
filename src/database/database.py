import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

database_url = os.getenv('DATABASE_URL')
print(database_url)
engine = create_engine(database_url)
session = sessionmaker(bind=engine, expire_on_commit=False)


def connection(func):
    def wrapper(*args, **kwargs):
        with session() as conn:
            return func(conn, *args, **kwargs)

    return wrapper


def create_tables():
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
