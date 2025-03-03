from pydantic import BaseModel, field_validator
from typing import List, Optional

class SessionEmbeddings(BaseModel):
    index: int
    id_session: int
    texto: str
    embeddings: list[float]

    @field_validator('embeddings')
    def validate_embedding(cls, value):
        if not isinstance(value, list) or not all(isinstance(x, float) for x in value):
            raise ValueError("embedding must be a list of floats")
        return value
    
    class Config:
        from_attributes = True

# Define the request
class RetrieverRequest(BaseModel):
    prompt: str
    embedding: List[float]

# Define the response
class PromptResponse(BaseModel):
    prompt: str
    text: List[str]

class AugmentResponse(BaseModel):
    model: str
    prompt: str
    stream: bool
    context: List[str]
    response: str
    done: bool = False
    done_reason: Optional[str] = ""