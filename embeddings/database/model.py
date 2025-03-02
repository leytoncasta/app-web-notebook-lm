from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from database.db import Base

class FilesDB(Base):
    __tablename__ = "session_embeddings"
    __table_args__ = {"schema": "vectorial"}

    index = Column(Integer, primary_key=True)
    id_session = Column(Integer, nullable=False)
    texto = Column(Text, nullable=False)
    embeddings = Column(ARRAY(FLOAT), nullable=False)
