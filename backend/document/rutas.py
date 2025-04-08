from fastapi import APIRouter, Depends, UploadFile, status, Form
from JWT.auth import verify_token
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
PATH_FILESTORE = os.getenv("PATH_FILESTORE")
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
        if PATH_FILESTORE:
            #cretae chat_id as a specific diectory if it does not exist
            chat_folder = os.path.join(PATH_FILESTORE, str(chat_id))
            os.makedirs(chat_folder, exist_ok=True)

            # Save file in the chat_id folder
            file_location = os.path.join(chat_folder, file_upload.filename)
            with open(file_location, "wb+") as file_object:
                file_object.write(file_upload.file.read())
            
            await file_upload.seek(0)  # Reset file pointer to the beginning
            logger.info(f"File saved at {file_location}")
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
