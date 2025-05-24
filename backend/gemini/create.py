from sqlalchemy.orm import Session
from . import model

def write_db(db: Session, chat_id, message, status_code, date):
    db_ins = model.PromptResponseDB(chat_id=chat_id, message=message, status_code=status_code, date=date)
    db.add(db_ins)
    db.commit()
    db.refresh(db_ins)
    return db_ins
