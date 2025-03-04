from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contexto import model
from contexto.path import router as retriever_router
from database import engine
import uvicorn

model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contexto App",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://embeddings2:8002"],  # embedding url (need to be define)
    allow_credentials=True,
    allow_methods=["POST"],  # Allows just POST method
    allow_headers=["*"],  # Allows all headers
)

app.include_router(retriever_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
