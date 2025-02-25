from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

app = FastAPI()

class LLMQuery(BaseModel):
    model: str
    prompt: str
    stream: bool
    context: list

@app.post("/generate")
async def generate(query: LLMQuery):

    try:
        async with httpx.AsyncClient() as client:
            # Forward the payload to the Ollama LLM service
            response = await client.post(OLLAMA_API_URL, json=query.dict())
            response.raise_for_status()
            data = response.json()
            
            # Forward the response to the backend
            backend_payload = {"data": data["response"]}
            backend_response = await client.post(BACKEND_API_URL, json=backend_payload)
            backend_response.raise_for_status()
            
            return data
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Ollama service: {e}")