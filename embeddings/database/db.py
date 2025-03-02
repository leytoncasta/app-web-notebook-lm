from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(os.path.join("database", ".env"), override=True)

print(os.getenv("CONNECTION_STRING"))

engine = create_engine(os.getenv("CONNECTION_STRING"), connect_args={"options": "-c client_encoding=UTF8"})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(f"Error al obtener la sesión de la base de datos: {e}")
        raise
    finally:
        db.close()
