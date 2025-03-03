from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from usuario import modelo
from usuario.rutas import router as usuario_router
from LLM.rutas import router as LLM_router
from chat.rutas import router as chat_router
from document.rutas import router as document_router
from prompt.rutas import router as prompt_router
from database import engine

modelo.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LLM App",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(usuario_router)
app.include_router(LLM_router)
app.include_router(chat_router)
app.include_router(document_router)
app.include_router(prompt_router)