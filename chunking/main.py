import json
import logging
import os
import traceback
from pathlib import Path
from typing import List

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from google.cloud import storage
from pypdf import PdfReader

# ---------------
# Configuración
# ---------------

PROJECT_ID = "desarrollo-cloud-457900"
EMBEDDING_SERVICE_URL = "http://10.109.2.15:80/generate_embeddings"  # "http://10.109.2.13:8002/generate_embeddings"

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)
CLOUD_STORAGE = os.getenv("CLOUD_STORAGE")

app = FastAPI()
logger = logging.getLogger("uvicorn")

# ---------------
# Procesamiento
# ---------------


async def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


async def process_message(file, chat_id):
    try:
        pdf_reader = PdfReader(file)
        text = " ".join(
            [page.extract_text() for page in pdf_reader.pages if page.extract_text()]
        )
        chunks = await chunk_text(text)

        async with aiohttp.ClientSession() as session:
            json_document = {"chunks": chunks, "chat_id": chat_id}
            try:
                async with session.post(
                    EMBEDDING_SERVICE_URL, json=json_document
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"[Embeddings] Falló conexión a {EMBEDDING_SERVICE_URL} (status={response.status}) para chat_id={chat_id}"
                        )
                    else:
                        logger.info(
                            f"[Embeddings] POST exitoso a {EMBEDDING_SERVICE_URL} para chat_id={chat_id}"
                        )
            except Exception as e:
                logger.error(f"[Embeddings] Error de conexión al servicio: {e}")
                logger.debug(traceback.format_exc())

    except Exception as e:
        logger.error(
            f"[process_message] Error al procesar archivo PDF para chat_id={chat_id}: {e}"
        )
        logger.debug(traceback.format_exc())


# ---------------
# Endpoint Push
# ---------------


@app.post("/pubsub/push")
async def receive_pubsub_push(request: Request):
    try:
        body = await request.json()
        message_data = body.get("message", {}).get("data")
        if not message_data:
            raise HTTPException(status_code=400, detail="Falta 'data' en mensaje")

        message_json = json.loads(base64_decode(message_data).decode("utf-8"))
        file_name = message_json.get("file_name")
        chat_id = message_json.get("chat_id")

        if not file_name or not chat_id:
            logger.error(
                f"[Pub/Sub Push] Faltan datos: file_name={file_name}, chat_id={chat_id}"
            )
            return {"status": "error", "reason": "missing fields"}

        local_path = f"/tmp/{file_name}"
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(CLOUD_STORAGE)
            blob_path = f"{chat_id}/{file_name}"
            blob = bucket.blob(blob_path)
            blob.download_to_filename(local_path)
            logger.info(f"[Cloud Storage] Archivo descargado: {local_path}")
        except Exception as e:
            logger.error(f"[Cloud Storage] Error al descargar archivo: {e}")
            logger.debug(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error al descargar archivo")

        try:
            with open(local_path, "rb") as file:
                await process_message(file, chat_id)
                logger.info(f"[Proceso] Archivo procesado: {local_path}")
        except Exception as e:
            logger.error(f"[Proceso] Error procesando archivo local: {e}")
            logger.debug(traceback.format_exc())

        if os.path.exists(local_path):
            os.remove(local_path)
            logger.info(f"[Cleanup] Archivo eliminado: {local_path}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"[Pub/Sub Push] Error general: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error interno")


# ---------------
# Utilidades
# ---------------

import base64


def base64_decode(data: str) -> bytes:
    """Decodifica una cadena base64 con padding automático."""
    data += "=" * (-len(data) % 4)
    return base64.b64decode(data)
