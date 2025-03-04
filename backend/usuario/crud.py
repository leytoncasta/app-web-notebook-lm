from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from . import modelo
from typing import List
from JWT.auth import (
    verify_password, 
    get_password_hash, 
    create_access_token,
)

def login_usuario(db: Session, username: str, password: str):
    """Login function that accepts OAuth2 standard fields (username, password)"""
    usuario = db.query(modelo.UsuarioDB).filter(
        modelo.UsuarioDB.nombre_usuario == username
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    if not verify_password(password, usuario.contraseña):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    access_token = create_access_token(
        data={"sub": usuario.nombre_usuario}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario
    }

def crear_usuario(db: Session, usuario: modelo.UsuarioDB):
    db_usuario = db.query(modelo.UsuarioDB).filter(
        modelo.UsuarioDB.nombre_usuario == usuario.nombre_usuario
    ).first()
    
    if db_usuario:
        raise HTTPException(status_code=400, detail="Nombre de usuario ya existe")
    
    # Hash the password before storing
    usuario_dict = usuario.dict()
    usuario_dict["contraseña"] = get_password_hash(usuario_dict["contraseña"])
    
    db_usuario = modelo.UsuarioDB(**usuario_dict)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def obtener_usuarios(db: Session) -> List[modelo.UsuarioDB]:
    return db.query(modelo.UsuarioDB).all()

def obtener_usuario(db: Session, usuario_id: int):
    db_usuario = db.query(modelo.UsuarioDB).filter(modelo.UsuarioDB.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

def actualizar_usuario(db: Session, usuario_id: int, usuario: modelo.UsuarioDB):
    db_usuario = db.query(modelo.UsuarioDB).filter(modelo.UsuarioDB.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Verificar si el nuevo nombre de usuario ya existe
    usuario_existente = db.query(modelo.UsuarioDB).filter(
        modelo.UsuarioDB.nombre_usuario == usuario.nombre_usuario,
        modelo.UsuarioDB.id != usuario_id
    ).first()
    
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Nombre de usuario ya existe")
    
    for key, value in usuario.dict(exclude_unset=True).items():
        setattr(db_usuario, key, value)
    
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def eliminar_usuario(db: Session, usuario_id: int):
    db_usuario = db.query(modelo.UsuarioDB).filter(modelo.UsuarioDB.id == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(db_usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado exitosamente"}