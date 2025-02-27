from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from . import crud, schema
from JWT.auth import verify_token

router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)

@router.post("/", response_model=schema.Chat, status_code=status.HTTP_201_CREATED)
def create_chat(chat: schema.ChatCreate, db: Session = Depends(get_db), _: dict = Depends(verify_token)):
    return crud.create_chat(db=db, chat=chat)

@router.get("/{chat_id}", response_model=schema.Chat, status_code=status.HTTP_200_OK)
def read_chat(chat_id: int, db: Session = Depends(get_db), _: dict = Depends(verify_token)):
    db_chat = crud.get_chat(db, chat_id=chat_id)
    if db_chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return db_chat

@router.get("/", response_model=List[schema.Chat], status_code=status.HTTP_200_OK)
def read_chats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    chats = crud.get_all_chats(db, skip=skip, limit=limit)
    return chats

@router.delete("/{chat_id}", response_model=bool, status_code=status.HTTP_200_OK)
def delete_chat(chat_id: int, db: Session = Depends(get_db), _: dict = Depends(verify_token)):
    result = crud.delete_chat(db, chat_id=chat_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return True

@router.get("/user/{user_id}", response_model=List[schema.Chat], status_code=status.HTTP_200_OK)
def read_user_chats(
    user_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    _: dict = Depends(verify_token)
):
    chats = crud.get_chats_by_user_id(db, user_id=user_id, skip=skip, limit=limit)
    if not chats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No chats found for user {user_id}"
        )
    return chats