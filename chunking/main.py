from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pypdf import PdfReader
from typing import List, Dict, Any
import httpx

app = FastAPI()

EMBEDDING_SERVICE_URL = "http://embeddings1:8002/generate_embeddings"

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Divide el texto en fragmentos de tamaño determinado."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...), chat_id: int = Form(...)) -> Dict[str, Any]:
    """Recibe un PDF, extrae el texto, lo divide en fragmentos y los envía al servicio de embeddings junto con el chat_id."""
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
        
        pdf_reader = PdfReader(file.file)
        text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        
        if not text:
            return {"error": "No se pudo extraer texto del PDF"}
        
        chunks = chunk_text(text)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(EMBEDDING_SERVICE_URL, json={"chat_id": chat_id, "chunks": chunks})
            embeddings_response = response.json()
        
        return embeddings_response
    except Exception as e:
        return {"error": str(e)}