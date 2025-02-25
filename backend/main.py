from fastapi import FastAPI, Depends

from database import engine, get_db
from usuario import modelo, crud
from usuario import shema

from sqlalchemy.orm import Session
from typing import List

modelo.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Wiiii"}

@app.post("/usuarios/", response_model=shema.Usuario)
async def crear_usuario(usuario: shema.Usuario, db: Session = Depends(get_db)):
    return crud.crear_usuario(db, usuario)

@app.get("/usuarios/", response_model=List[shema.Usuario])
async def obtener_usuarios(db: Session = Depends(get_db)):
    return crud.obtener_usuarios(db)

@app.get("/usuarios/{usuario_id}", response_model=shema.Usuario)
async def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return crud.obtener_usuario(db, usuario_id)

@app.put("/usuarios/{usuario_id}", response_model=shema.Usuario)
async def actualizar_usuario(usuario_id: int, usuario: shema.Usuario, db: Session = Depends(get_db)):
    return crud.actualizar_usuario(db, usuario_id, usuario)

@app.delete("/usuarios/{usuario_id}")
async def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return crud.eliminar_usuario(db, usuario_id)