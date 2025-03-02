from fastapi import APIRouter, Depends, UploadFile, status, Form
from JWT.auth import verify_token
import httpx

router = APIRouter(
    prefix="/documentos",
    tags=["documentos"]
)

CHUNKING_SERVICE_URL = "http://chunking:8001/upload_document"

@router.post("/uploadfile", status_code=status.HTTP_200_OK)
async def subir_documento(
    file_upload: UploadFile, 
    chat_id: int = Form(...),
    _: dict = Depends(verify_token)
):
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

