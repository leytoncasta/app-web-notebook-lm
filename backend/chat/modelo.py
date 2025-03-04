from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class UsuarioDB(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id"), index=True)