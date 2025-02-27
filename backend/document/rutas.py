from fastapi import APIRouter, Depends, UploadFile, status
from JWT.auth import verify_token

router = APIRouter(
    prefix="/documentos",
    tags=["documentos"]
)


@router.post("/uploadfile", status_code=status.HTTP_201_CREATED)
async def subir_documento(file_upload: UploadFile, _: dict = Depends(verify_token),):
    print ("filename", file_upload.filename)
    return {"filename": file_upload.filename}

