from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from sentence_transformers import SentenceTransformer
from database.db import get_db
from database.model import FilesDB
from database import model as modelo
from database import engine

# ---------------
# FastAPI
# ---------------

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")  # paraphrase-MiniLM-L3-v2
modelo.Base.metadata.create_all(bind=engine)
API_URL_RETRIEVER = "http://retriever:8080/retriever/contexto"

class EmbeddingRequest(BaseModel):
    chat_id: int
    chunks: List[str]

@app.post("/generate_embeddings")
async def generate_embeddings(data: EmbeddingRequest, db: Session = Depends(get_db)):

    try:
        chat_id = data.chat_id
        chunks = data.chunks or []

        if not chunks:
            raise HTTPException(status_code=400, detail="No hay fragmentos de texto para procesar.")

        embeddings = model.encode(chunks).tolist()
        results = []

        for chunk, embedding in zip(chunks, embeddings):
            db_entry = FilesDB(id_session=chat_id, texto=chunk, embeddings=embedding)
            db.add(db_entry)
            results.append({"chunk": chunk, "embedding": embedding})

        db.commit()  

        return {"chat_id": chat_id, "num_chunks": len(chunks), "data": results}

    except Exception as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail=str(e))