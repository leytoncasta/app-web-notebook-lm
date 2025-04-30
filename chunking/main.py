from fastapi import FastAPI
from pypdf import PdfReader
from typing import List

from dotenv import load_dotenv
from pathlib import Path
import logging
import os

from google.cloud import pubsub_v1
import aiohttp
import asyncio
import json

from google.cloud import storage

# ---------------
# Configuración
# ---------------

PROJECT_ID = "desarrollo-cloud-457900"
SUBSCRIPTION_ID = "webserver-to-chunking-sub"



EMBEDDING_SERVICE_URL = "http://embeddings:8002/generate_embeddings"



subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)
CLOUD_STORAGE = os.getenv("CLOUD_STORAGE")

app = FastAPI()
logger = logging.getLogger("uvicorn")

# ---------------
# Procesamiento asincrónico
# ---------------

async def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

async def process_message(file, chat_id):

    pdf_reader = PdfReader(file)
    text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    
    chunks = await chunk_text(text)
    
    async with aiohttp.ClientSession() as session:
        json_document = {
            "chunks": chunks,
            "chat_id": chat_id,
        }
        async with session.post(EMBEDDING_SERVICE_URL, json=json_document) as response:
            pass

# ---------------
# Polling manual desde Pub/Sub
# ---------------

async def pull_messages_loop():
    
    while True:
        try:

            # Leemos los mensajes 
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

                # Descargar el archivo de Google Cloud Storage
                file_name = message.get("file_name")
                chat_id = message.get("chat_id")

                if not file_name or not chat_id:
                    logger.error(f"Faltan datos en el mensaje: file_name={file_name}, chat_id={chat_id}")
                    ack_ids.append(received_message.ack_id)
                    continue

                storage_client = storage.Client()
                bucket = storage_client.bucket(CLOUD_STORAGE)
                folder_prefix = f"{str(chat_id)}/"

                local_path = f"/tmp/{file_name}"
                blob = bucket.blob(f"{folder_prefix}{file_name}")
                blob.download_to_filename(local_path)
                logger.info(f"Downloaded file to: {local_path}")

                with open(local_path, "rb") as file:
                    await process_message(file, chat_id)
                    logger.info(f"Send local file: {local_path}")

                ack_ids.append(received_message.ack_id)

                if os.path.exists(local_path):
                    os.remove(local_path)
                    logger.info(f"Deleted local file: {local_path}")

            if ack_ids:
                subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": ack_ids,
                    }
                )

        except Exception as e:
            logger.error(f"Error en pull loop: {e}")

        await asyncio.sleep(0.1)

# ---------------
# Startup de FastAPI
# ---------------

@app.on_event("startup")
async def startup_event():
    print("Escuchando mensajes...", flush=True)
    asyncio.create_task(pull_messages_loop())