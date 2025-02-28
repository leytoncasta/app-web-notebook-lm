from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contexto import model
from contexto.path import router as retriever_router
from database import engine

model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contexto App",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # embedding url (need to be define)
    allow_credentials=True,
    allow_methods=["POST"],  # Allows just POST method
    allow_headers=["*"],  # Allows all headers
)

app.include_router(retriever_router)
