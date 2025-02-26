from pydantic import BaseModel

# Schema for creating a new chat
class ChatCreate(BaseModel):
    id_usuario: int

# Schema for reading chat data
class Chat(BaseModel):
    id: int
    id_usuario: int

    class Config:
        from_attributes = True