from pydantic import BaseModel 
from typing import List, Optional

class AugmentRequest(BaseModel):
    prompt: str
    text: List[str]
    chat_id: int