from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader
from typing import List
from sentence_transformers import SentenceTransformer
app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")  


@app.post("/generate_embeddings")
async def generate_embeddings(chunks: List[str]):
    """Recibe fragmentos de texto y devuelve una lista de (embedding, chunk original)."""
    try:
        embeddings = model.encode(chunks).tolist()
        result = [{"chunk": chunk, "embedding": embedding} for chunk, embedding in zip(chunks, embeddings)]
        return {"num_chunks": len(chunks), "data": result}
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