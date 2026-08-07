import os
from typing import Annotated
 
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import text
from sqlmodel import Session, create_engine



## Database setup
load_dotenv()  # Retrieve DB variables in .env

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# Connect to MySQL server (no database specified) to check/create the database
def create_database_if_not_exists():
    server_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    temp_engine = create_engine(server_url)
    with temp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4"))
        conn.commit()
    temp_engine.dispose()


# Create engine and connect to MySQL
# echo=True -> print executed SQL statements
mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(mysql_url, echo=False)


# DB session dependency
def get_session():
    with Session(engine) as session:
        yield session


# Reusable type alias for the Session dependency
SessionDep = Annotated[Session, Depends(get_session)]