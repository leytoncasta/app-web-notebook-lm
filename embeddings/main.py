from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader
from typing import List
from sentence_transformers import SentenceTransformer
app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")  


@app.post("/generate_embeddings")
async def generate_embeddings(chunks: List[str]):
    """Recibe fragmentos de texto y devuelve sus embeddings."""
    try:
        embeddings = model.encode(chunks).tolist()  # Convertir a listas para JSON
        return {"num_chunks": len(chunks), "embeddings": embeddings}
    except Exception as e:
        return {"error": str(e)}