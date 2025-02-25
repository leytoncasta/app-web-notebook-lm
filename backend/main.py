from fastapi import FastAPI
from usuario import modelo
from usuario.rutas import router as usuario_router
from database import engine

modelo.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LLM App",
    version="1.0.0"
)

app.include_router(usuario_router)