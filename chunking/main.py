from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader
from typing import List
import httpx

app = FastAPI()

EMBEDDING_SERVICE_URL = "http://embeddings:8002/generate_embeddings"

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Divide el texto en fragmentos de tamaño determinado."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """Recibe un PDF, extrae el texto, lo divide en fragmentos y los envía al servicio de embeddings."""
    try:
        pdf_reader = PdfReader(file.file)
        text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        
        if not text:
            return {"error": "No se pudo extraer texto del PDF"}

        chunks = chunk_text(text)

        async with httpx.AsyncClient() as client:
            response = await client.post(EMBEDDING_SERVICE_URL, json=chunks)  # Enviar la lista directamente
            embeddings_response = response.json()

        return embeddings_response
    except Exception as e:
        return {"error": str(e)}