from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from pypdf import PdfReader
from typing import List, Dict
from sentence_transformers import SentenceTransformer

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")  


class EmbeddingRequest(BaseModel):
    chat_id: str
    chunks: List[str]

@app.post("/generate_embeddings")
async def generate_embeddings(data: EmbeddingRequest):
    """Recibe fragmentos de texto y devuelve embeddings junto con el chat_id."""
    try:
        chat_id = data.chat_id  # Acceder directamente sin .get()
        chunks = data.chunks or []

        if not chunks:
            return {"error": "No hay fragmentos de texto para procesar."}

        embeddings = model.encode(chunks).tolist()
        result = [{"chunk": chunk, "embedding": embedding} for chunk, embedding in zip(chunks, embeddings)]

        return {"chat_id": chat_id, "num_chunks": len(chunks), "data": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/embed_text")
async def embed_text(text: str):
    """Recibe un texto y devuelve su embedding."""
    try:
        embedding = model.encode(text).tolist()  
        return {"embedding": embedding}
    except Exception as e:
        return {"error": str(e)}