import aiohttp
from pathlib import Path
import os
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_ABSOLUTE_PATH = Path(__file__).resolve().parent
env_file = SERVICE_ABSOLUTE_PATH / '.env'
load_dotenv(env_file)

API_URL_LLM = os.getenv("API_URL_LLM")
if not API_URL_LLM:
    raise ValueError("API_URL_LLM environment variable is not set")

async def post_searching(payload: Dict[str, Any]) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL_LLM, json=payload) as response:
                response.raise_for_status()
                logger.info("Successfully consumed llm service")
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Failed to consume augmenter service: {str(e)}")
            raise HTTPException(
                status_code=getattr(response, 'status', 500),
                detail=f"External service error: {str(e)}"
            )