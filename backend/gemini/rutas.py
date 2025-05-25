from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict
from datetime import datetime
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import create
import pytz
import base64
import json

from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists

router = APIRouter(
    prefix="/LLM",
    tags=["LLM"]
)

# ---------------
# CONFIGURACIÓN FIJA
# ---------------

PROJECT_ID = "desarrollo-cloud-457900"
TOPIC_ID = "workers-to-webserver"
SUBSCRIPTION_ID = "embedding2-to-cloudrun-push"
PUSH_ENDPOINT = "https://backend-service-697367184851.us-central1.run.app/LLM/pubsub/push"

# ---------------
# CREAR SUSCRIPCIÓN PUSH (UNA SOLA VEZ)
# ---------------

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
topic_path = subscriber.topic_path(PROJECT_ID, TOPIC_ID)

def ensure_subscription_exists():
    try:
        subscriber.create_subscription(
            name=subscription_path,
            topic=topic_path,
            push_config={"push_endpoint": PUSH_ENDPOINT},
            ack_deadline_seconds=20,
        )
        print(f"Subscripción push creada: {subscription_path}", flush=True)
    except AlreadyExists:
        print(f"Subscripción ya existe: {subscription_path}", flush=True)

# Solo descomentá después del primer deploy, cuando tengas el endpoint real (huevo y gallina)
ensure_subscription_exists()

# ---------------
# ALMACÉN TEMPORAL DE RESPUESTAS
# ---------------

response_store: Dict[str, dict] = {}

async def process_message(data, chat_id):
    response_store[chat_id] = {
        "data": data,
        "timestamp": datetime.now(),
    }

# ---------------
# ENDPOINT PARA RECIBIR PUSH DE PUB/SUB
# ---------------

@router.post("/pubsub/push")
async def receive_pubsub_push(request: Request, db: Session = Depends(get_db)):
    try:
        timestamp = func.now()
    except Exception as e:
        print("Error procesando mensaje push:", e, flush=True)
        raise HTTPException(status_code=500, detail=f"Error timestamp: {e}")
    try:
        body = await request.json()
        message_data = body["message"]["data"]
        decoded = base64.b64decode(message_data).decode("utf-8")
        message = json.loads(decoded)

        print(f"Mensaje recibido via PUSH: {message}", flush=True)

        data = message.get("data")
        chat_id = str(message.get("chat_id"))

        await process_message(data, chat_id)
        # Guardar datos en la base de datos de PromptResponse
        create.write_db(db, int(chat_id), str(data), 201, timestamp)
        
        return {"status": "success"}

    except Exception as e:
        try:
            create.write_db(db, int(chat_id), str(data), 400, timestamp)
        except Exception as db_error:
            print("Error guardando en la base de datos:", db_error, flush=True)
        print("Error procesando mensaje push:", e, flush=True)
        raise HTTPException(status_code=400, detail="Error en el mensaje")

# ---------------
# ENDPOINT PARA CONSULTA DESDE FRONTEND
# ---------------

@router.get("/response/{chat_id}")
async def get_llm_response(chat_id: str):
    if chat_id not in response_store:
        return {"status": "waiting", "data": None}
    return {"status": "success", "data": response_store[chat_id]["data"]}

# ---------------
# LIMPIEZA DE DATOS ANTIGUOS
# ---------------

from fastapi_utils.tasks import repeat_every

@router.on_event("startup")
@repeat_every(seconds=600)
async def cleanup_old_responses():
    current_time = datetime.now()
    expired_chats = [chat_id for chat_id, data in response_store.items()
                     if (current_time - data["timestamp"]).seconds > 600]
    for chat_id in expired_chats:
        del response_store[chat_id]
