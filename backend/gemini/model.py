from sqlalchemy import Column, Integer, Text, TIMESTAMP
from database import Base

class PromptResponseDB(Base):
    __tablename__ = "prompt_response"

    message = Column(Text, nullable=False)
    chat_id = Column(Integer, nullable=False)
    status_code = Column(Integer, nullable=False)
    date = Column(TIMESTAMP, nullable=False)
