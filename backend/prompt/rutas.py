from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from JWT.auth import verify_token
import httpx

router = APIRouter(
    prefix="/prompt",
    tags=["prompt"]
)

class AugmentResponse(BaseModel):
    model: str
    prompt: str
    stream: bool
    context: List[str]
    response: str
    done: bool = False
    done_reason: Optional[str] = ""

class PromptRequest(BaseModel):
    text: str
    chat_id: int

EMBEDDING_SERVICE_URL = "http://embeddings2:8002/embed_text"

@router.post("/", response_model=AugmentResponse, status_code=status.HTTP_201_CREATED)
async def subir_prompt(
    request: PromptRequest,
    _: dict = Depends(verify_token)
):
    try:        
        payload = {
            "text": request.text,
            "chat_id": request.chat_id
        }

        async with httpx.AsyncClient(timeout=1000.0) as client:
            try:
                print(f"Attempting to connect to: {EMBEDDING_SERVICE_URL}")
                print(f"With payload: {payload}")
                
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                response = await client.post(
                    EMBEDDING_SERVICE_URL, 
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                
                return response.json()
                
            except httpx.TimeoutException as e:
                print(f"Timeout error: {str(e)}")
                raise HTTPException(status_code=504, detail="Request timed out")
            except httpx.RequestError as e:
                print(f"Request error: {str(e)}")
                raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")
            except httpx.HTTPStatusError as e:
                print(f"HTTP error: {str(e)}")
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Embedding service error: {e.response.text}"
                )
    
    except Exception as e:
        print(f"General error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))