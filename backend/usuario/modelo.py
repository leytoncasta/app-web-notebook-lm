from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from database import Base

class UsuarioDB(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, unique=True, index=True)
    contraseña = Column(String)

class Usuario(BaseModel):
    id: int | None = None
    nombre_usuario: str
    contraseña: str

    class Config:
        from_attributes = True