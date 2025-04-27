from fastapi import APIRouter, Depends, UploadFile, status, Form
from JWT.auth import verify_token
from google.cloud import storage
import httpx

from pathlib import Path
from dotenv import load_dotenv
import os
import logging

router = APIRouter(
    prefix="/documentos",
    tags=["documentos"]
)

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

DOCUMENT_URL = os.getenv("DOCUMENT_URL") 
CLOUD_STORAGE = os.getenv("PATH_FILESTORE")
CHUNKING_SERVICE_URL = f"{DOCUMENT_URL}/upload_document"

logger = logging.getLogger("uvicorn")
logger.info(f"Document URL: {CHUNKING_SERVICE_URL}")
print(f"Document URL: {CHUNKING_SERVICE_URL}")

@router.post("/uploadfile", status_code=status.HTTP_200_OK)
async def subir_documento(
    file_upload: UploadFile, 
    chat_id: int = Form(...),
    _: dict = Depends(verify_token)
):
    # Saving file in filestore
    try:
        if CLOUD_STORAGE:
            storage_client = storage.Client()
            bucket = storage_client.bucket(CLOUD_STORAGE)
            blobs = list(bucket.list_blobs(prefix=chat_id+"/", max_results=1))
            if not blobs:
                blob = bucket.blob(chat_id+"/")
                blob.upload_from_file(file_upload.file, content_type=file_upload.content_type)
                logger.info(f"Created folder: gs://{CLOUD_STORAGE}/{chat_id+"/"}")
            else:
                blob = bucket.blob(chat_id+"/")
                blob.upload_from_file(file_upload.file, content_type=file_upload.content_type)
                logger.info(f"Updated folder: gs://{CLOUD_STORAGE}/{chat_id+"/"}")
    except Exception as e:
        logger.error(f"Error saving file: {e}")

    try:        
        files = {"file": (file_upload.filename, file_upload.file, file_upload.content_type)}
        data = {"chat_id": chat_id}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                CHUNKING_SERVICE_URL,
                files=files,
                data=data
            )
            
        return {
            "filename": file_upload.filename,
            "status": "success",
            "response": response.json()
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
