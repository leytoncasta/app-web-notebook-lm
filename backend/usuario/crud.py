from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import modelo
from typing import List

def crear_usuario(db: Session, usuario: modelo.UsuarioDB):
    db_usuario = db.query(modelo.UsuarioDB).filter(
        modelo.UsuarioDB.nombre_usuario == usuario.nombre_usuario
    ).first()
    
    if db_usuario:
        raise HTTPException(status_code=400, detail="Nombre de usuario ya existe")
    
    db_usuario = modelo.UsuarioDB(**usuario.dict())
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