from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import read, schema
from database import get_db

# Define the FastAPI router
router = APIRouter(
    prefix="/retriever",
    tags=["retriever"]
)

# Define the POST method
@router.post("/contexto", response_model=schema.PromptResponse, status_code=status.HTTP_200_OK)
def prompt_retriever(request: schema.RetrieverRequest, db: Session = Depends(get_db)):
    try:
        # Call the function to get textos based on the embedding
        textos = read.get_texts_by_embedding(db, request.embedding)

        # Return the prompt and the textos
        return schema.PromptResponse(prompt=request.prompt, textos=textos)
    
    except ValueError as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
