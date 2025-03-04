from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi_utils.tasks import repeat_every 
from typing import Dict
from datetime import datetime
class LLMRequest(BaseModel):
    data: str
    chat_id: int

router = APIRouter(
    prefix="/LLM",
    tags=["LLM"]
)

response_store: Dict[str, dict] = {}

@router.post("/response")
async def receive_llm_response(request: LLMRequest):
    try:
        print(f"Received response: {request.data}")
        response_store[request.chat_id] = {
            "data": request.data,
            "timestamp": datetime.now(),
        }
        print(f"Stored response for chat_id: {response_store}")
        return {"status": "received", "chat_id": request.chat_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request data")

@router.get("/response/{chat_id}")
async def get_llm_response(chat_id: str):
    try:
        chat_id = int(chat_id)
        if chat_id not in list(response_store.keys()):
            return {"status": "waiting", "data": None}
        
        response = response_store[chat_id]["data"]
        return {"status": "success", "data": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving response")

@router.on_event("startup")
@repeat_every(seconds=1000) 
async def cleanup_old_responses():
    current_time = datetime.now()
    expired_chats = [
        chat_id for chat_id, data in response_store.items()
        if (current_time - data["timestamp"]).seconds > 300
    ]
    for chat_id in expired_chats:
        del response_store[chat_id]