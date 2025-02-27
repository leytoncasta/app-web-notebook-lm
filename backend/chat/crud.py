from sqlalchemy.orm import Session
from . import modelo, schema

def create_chat(db: Session, chat: schema.ChatCreate):
    db_chat = modelo.UsuarioDB(id_usuario=chat.id_usuario)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_chat(db: Session, chat_id: int):
    return db.query(modelo.UsuarioDB).filter(modelo.UsuarioDB.id == chat_id).first()

def get_all_chats(db: Session, skip: int = 0, limit: int = 100):
    return db.query(modelo.UsuarioDB).offset(skip).limit(limit).all()

def delete_chat(db: Session, chat_id: int):
    db_chat = db.query(modelo.UsuarioDB).filter(modelo.UsuarioDB.id == chat_id).first()
    if db_chat:
        db.delete(db_chat)
        db.commit()
        return True
    return False

def get_chats_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(modelo.UsuarioDB)\
        .filter(modelo.UsuarioDB.id_usuario == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()