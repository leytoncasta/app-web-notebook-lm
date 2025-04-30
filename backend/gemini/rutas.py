from fastapi import APIRouter, HTTPException
from fastapi_utils.tasks import repeat_every
from typing import Dict
from datetime import datetime

from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists
import threading
import asyncio
import requests
import json

router = APIRouter(
    prefix="/LLM",
    tags=["LLM"]
)

# ---------------
# PUB/SUB CONFIG
# ---------------

PROJECT_ID = "desarrollo-cloud-457900"
TOPIC_ID = "workers-to-webserver"
subscriber = pubsub_v1.SubscriberClient()

def get_instance_name():
    metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/name"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    return response.text.strip()  # Ej: 'webserver-group-xyz123'

def get_subscription_id(instance_name: str) -> str:
    return f"embedding2-to-{instance_name}"

def ensure_subscription_exists(subscriber, subscription_path, topic_path):
    try:
        subscriber.create_subscription(
            name=subscription_path,
            topic=topic_path,
            ack_deadline_seconds=20,
        )
        print(f"Subscripción creada: {subscription_path}", flush=True)
    except AlreadyExists:
        print(f"Subscripción ya existe: {subscription_path}", flush=True)

instance_name = get_instance_name()
SUBSCRIPTION_ID = get_subscription_id(instance_name)
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)
topic_path = subscriber.topic_path(PROJECT_ID, TOPIC_ID)

ensure_subscription_exists(subscriber, subscription_path, topic_path)

# ---------------
# IN-MEMORY RESPONSE STORE
# ---------------

response_store: Dict[str, dict] = {}

async def process_message(data, chat_id):
    try:
        response_store[chat_id] = {
            "data": data,
            "timestamp": datetime.now(),
        }
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request data")

# ---------------
# POLLING LOOP
# ---------------

async def pull_messages_loop():
    while True:
        try:
            response = subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": 10,
                    "return_immediately": False,
                },
                timeout=10
            )

            ack_ids = []

            for received_message in response.received_messages:
                message = json.loads(received_message.message.data.decode("utf-8"))
                print(f"Mensaje recibido: {message}", flush=True)

                data = message.get("data")
                chat_id = message.get("chat_id")
                await process_message(data, chat_id)

                ack_ids.append(received_message.ack_id)

            if ack_ids:
                subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": ack_ids,
                    }
                )

        except Exception as e:
            print(f"Error en pull loop: {e}", flush=True)

        await asyncio.sleep(1)

def start_polling_thread():
    asyncio.run(pull_messages_loop())

# ---------------
# STARTUP EVENTS
# ---------------

@router.on_event("startup")
async def startup_event():
    print(f"Instancia {instance_name} escuchando en {SUBSCRIPTION_ID}", flush=True)
    threading.Thread(target=start_polling_thread, daemon=True).start()

# ---------------
# FRONTEND API (opcional)
# ---------------

@router.get("/response/{chat_id}")
async def get_llm_response(chat_id: str):
    try:
        chat_id = int(chat_id)
        if chat_id not in response_store:
            return {"status": "waiting", "data": None}
        response = response_store[chat_id]["data"]
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving response")

# ---------------
# LIMPIEZA DE RESPUESTAS ANTIGUAS
# ---------------

@router.on_event("startup")
@repeat_every(seconds=600)
async def cleanup_old_responses():
    current_time = datetime.now()
    expired_chats = [chat_id for chat_id, data in response_store.items()
                     if (current_time - data["timestamp"]).seconds > 600]
    for chat_id in expired_chats:
        del response_store[chat_id]
