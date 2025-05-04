from fastapi import APIRouter, status, HTTPException
import os
from . import schema
from .question import structure_question
import logging

import google.generativeai as genai

from google.cloud import pubsub_v1
import json

api_key = os.getenv("API_KEY")

router = APIRouter(
    prefix="/augment",
    tags=["augment"]
)

logger = logging.getLogger(__name__)

PROJECT_ID = "desarrollo-cloud-457900"
TOPIC_ID = "workers-to-webserver"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def augment_search(request: schema.AugmentRequest):
    
    logger.info(f"Received request: {request}")
    try:
        genai.configure(api_key=api_key)
        model = "gemini-1.5-flash"

        prompt = structure_question(request.text, request.prompt)
        llm_response = genai.GenerativeModel(model).generate_content(prompt)

        try:
            payload = {
                "data": llm_response.text,
                "chat_id": request.chat_id
            }

            # Publicar en Pub/Sub
            future = publisher.publish(
                topic_path,
                data=json.dumps(payload).encode("utf-8")
            )
            message_id = future.result()
            print(f"Mensaje publicado con ID: {message_id}")

        except Exception as e:
            print(f"Error al publicar en Pub/Sub: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

          
    except ValueError as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))