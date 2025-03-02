from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

ABSOLUTE_PATH = Path(__file__).resolve().parent
env_file = ABSOLUTE_PATH / '.env'
load_dotenv(env_file)

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

engine = create_engine(
    CONNECTION_STRING,
    connect_args={"options": "-c client_encoding=UTF8"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()