import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'questbot')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME', 'questbot')

database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print(f"Connecting to: {database_url.replace(db_password, '*****')}")

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
