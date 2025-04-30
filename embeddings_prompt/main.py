from fastapi import FastAPI
from google.cloud import pubsub_v1
import aiohttp
import asyncio
import json

# ---------------
# Configuración
# ---------------

PROJECT_ID = "desarrollo-cloud-457900"
SUBSCRIPTION_ID = "webserver-to-embedding2"
API_URL_RETRIEVER = "http://retriever:8080/retriever/contexto"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

app = FastAPI()

# ---------------
# Procesamiento asincrónico
# ---------------

async def process_message(message_data):
    print(f"Mensaje recibido: {message_data}")

    # TODO: Cambiar el modelo de embeddings aL CORRECTO.
    embedding = [1] * 384

    async with aiohttp.ClientSession() as session:
        json_document = {
            "prompt": message_data.get("text"),
            "chat_id": message_data.get("chat_id"),
            "embedding": embedding
        }
        async with session.post(API_URL_RETRIEVER, json=json_document) as response:
            pass

# ---------------
# Polling manual desde Pub/Sub
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
                await process_message(message)
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

        await asyncio.sleep(0.1)

# ---------------
# Startup de FastAPI
# ---------------

@app.on_event("startup")
async def startup_event():
    print("Escuchando mensajes...", flush=True)
    asyncio.create_task(pull_messages_loop())
