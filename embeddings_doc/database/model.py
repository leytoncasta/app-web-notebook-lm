from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY
from database.db import Base
from sqlalchemy import Float
class FilesDB(Base):
    __tablename__ = "session_embeddings"
    __table_args__ = {"schema": "vectorial"}

    index = Column(Integer, primary_key=True)
    id_session = Column(Integer, nullable=False)
    texto = Column(Text, nullable=False)
    embeddings = Column(ARRAY(Float), nullable=False)
