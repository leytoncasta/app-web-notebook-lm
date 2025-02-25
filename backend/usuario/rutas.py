from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from . import crud, schema
from database import get_db
from JWT.auth import verify_token

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    credentials: schema.LoginSchema,
    db: Session = Depends(get_db)
):
    return crud.login_usuario(db, credentials.username, credentials.password)

@router.post("/", response_model=schema.Usuario, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: schema.Usuario, db: Session = Depends(get_db)):
    return crud.crear_usuario(db, usuario)

@router.get("/", response_model=List[schema.Usuario], status_code=status.HTTP_200_OK)
async def obtener_usuarios(db: Session = Depends(get_db)):
    return crud.obtener_usuarios(db)

@router.get("/{usuario_id}", response_model=schema.Usuario, status_code=status.HTTP_200_OK)
async def obtener_usuario(
    usuario_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return crud.obtener_usuario(db, usuario_id)

@router.put("/{usuario_id}", response_model=schema.Usuario, status_code=status.HTTP_200_OK)
async def actualizar_usuario(
    usuario_id: int,
    usuario: schema.Usuario,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return crud.actualizar_usuario(db, usuario_id, usuario)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(
    usuario_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return crud.eliminar_usuario(db, usuario_id)