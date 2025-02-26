from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from JWT.auth import verify_token

class LLMRequest(BaseModel):
    data: str

router = APIRouter(
    prefix="/LLM",
    tags=["LLM"]
)

@router.post("/response")
async def receive_llm_response(request: LLMRequest):
    try:
        return {"status": "received", "data": request.data}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request data")