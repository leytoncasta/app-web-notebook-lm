from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from JWT.auth import verify_token

from google.cloud import pubsub_v1
import json

router = APIRouter(
    prefix="/prompt",
    tags=["prompt"]
)
class PromptRequest(BaseModel):
    text: str
    chat_id: int

PROJECT_ID = "desarrollo-cloud-457900"
TOPIC_ID = "webserver-to-workers"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def subir_prompt(
    request: PromptRequest,
    _: dict = Depends(verify_token)
):
    try:
        payload = {
            "text": request.text,
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