from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from sentence_transformers import SentenceTransformer
from database.db import get_db
import random
from database.model import FilesDB
from database import model as modelo
from database import engine

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")  
modelo.Base.metadata.create_all(bind=engine)

class EmbeddingRequest(BaseModel):
    chat_id: int
    chunks: List[str]

@app.post("/insert_dummy_data")
async def insert_dummy_data(db: Session = Depends(get_db)):

    try:
        dummy_entry = FilesDB(
            id_session=random.randint(1, 100),
            texto="Texto de prueba",
            embeddings=[random.uniform(-1, 1) for _ in range(384)] 
        )
        
        db.add(dummy_entry)
        db.commit()

        return {"message": "Registro dummy insertado exitosamente."}
    
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    

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
    

class TextRequest(BaseModel):
    text: str

@app.post("/embed_text")
async def embed_text(request: TextRequest):
    try:
        embedding = model.encode(request.text).tolist()  
        return {"embedding": embedding}
    except Exception as e:
        return {"error": str(e)}