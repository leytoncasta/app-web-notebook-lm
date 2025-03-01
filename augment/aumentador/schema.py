from pydantic import BaseModel, field_validator

class AugmentRequest(BaseModel):
    prompt: str
    text: str

class AugmentResponse(BaseModel):
    question: str