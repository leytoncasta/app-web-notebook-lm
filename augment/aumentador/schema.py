from pydantic import BaseModel 
from typing import List, Optional

class AugmentRequest(BaseModel):
    prompt: str
    text: List[str]
    chat_id: int

class AugmentResponse(BaseModel):
    model: str
    prompt: str
    stream: bool
    context: List[str]
    response: str
    done: bool = False
    done_reason: Optional[str] = ""