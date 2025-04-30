from fastapi import APIRouter, Depends, UploadFile, status, Form
from JWT.auth import verify_token
from google.cloud import storage

from dotenv import load_dotenv
from pathlib import Path
import logging
import os

from google.cloud import pubsub_v1
import json

router = APIRouter(
    prefix="/documentos",
    tags=["documentos"]
)

logger = logging.getLogger("uvicorn")

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)
CLOUD_STORAGE = os.getenv("CLOUD_STORAGE")

PROJECT_ID = "desarrollo-cloud-457900"
TOPIC_ID = "webserver-to-chunking"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@router.post("/uploadfile", status_code=status.HTTP_200_OK)
async def subir_documento(file_upload: UploadFile, chat_id: int = Form(...), _: dict = Depends(verify_token)):
    
    # Vamos a guardar el archivo en el bucket de Google Cloud Storage
    # y luego lo subimos al servicio de chunking
    try:
        if CLOUD_STORAGE:

            storage_client = storage.Client()
            bucket = storage_client.bucket(CLOUD_STORAGE)
            folder_prefix = f"{str(chat_id)}/"

            blobs = list(bucket.list_blobs(prefix=folder_prefix, max_results=1))
            if not blobs:
                logger.info(f"Created folder: gs://{CLOUD_STORAGE}/{folder_prefix}")
            
            blob = bucket.blob(f"{folder_prefix}{file_upload.filename}")
            blob.upload_from_file(file_upload.file, content_type=file_upload.content_type)
            logger.info(f"Updated folder: gs://{CLOUD_STORAGE}/{folder_prefix}{file_upload.filename}")

            # -------------
            # Resgistrar en el Pub/Sub
            # -------------

            payload = {
                "file_name": file_upload.filename,
                "chat_id": chat_id
            }

            # Publicar en Pub/Sub
            future = publisher.publish(
                topic_path,
                data=json.dumps(payload).encode("utf-8")
            )
            message_id = future.result()
            print(f"Mensaje publicado con ID: {message_id}")

    except Exception as e:
        logger.error(f"Error saving file: {e}")