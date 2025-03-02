from pydantic import BaseModel 
from typing import List

class AugmentRequest(BaseModel):
    prompt: str
    text: List[str]

class AugmentResponse(BaseModel):
    model: str
    prompt: str
    stream: bool
    context: List[str]