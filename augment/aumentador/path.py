from fastapi import APIRouter, status, HTTPException
import httpx
import os
from . import schema
from .question import structure_question
import logging
import google.generativeai as genai

api_key = os.getenv("API_KEY")

router = APIRouter(
    prefix="/augment",
    tags=["augment"]
)

logger = logging.getLogger(__name__)
BACKEND_URL = "http://10.109.1.21:8000/LLM/response"

@router.post("/", response_model=schema.AugmentResponse, status_code=status.HTTP_201_CREATED)
async def augment_search(request: schema.AugmentRequest):
    logger.info(f"Received request: {request}")
    try:
        genai.configure(api_key=api_key)
        model = "gemini-1.5-flash"

        prompt = structure_question(request.text, request.prompt)

        llm_response = genai.GenerativeModel(model).generate_content(prompt)

        augment_response = schema.AugmentResponse(
            model=model,
            prompt=prompt,
            stream=False,                  
            context=request.text,                        
            response=llm_response.text,
            done=True,                         
            done_reason="stop"                
        )

        async with httpx.AsyncClient() as client:
            backend_response = await client.post(
                BACKEND_URL,
                json={
                    "data": llm_response.text,
                    "chat_id": request.chat_id
                }
            )
            if backend_response.status_code != 200:
                logger.error(f"Failed to send response to backend: {backend_response.text}")

        return augment_response
          
    except ValueError as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )