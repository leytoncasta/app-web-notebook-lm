from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import read, schema
from database import get_db
from service.api import post_contexts
import logging

# Define the FastAPI router
router = APIRouter(
    prefix="/retriever",
    tags=["retriever"]
)

# Set up logging
logger = logging.getLogger(__name__)

# Define the POST method
@router.post("/contexto", response_model=schema.PromptResponse, status_code=status.HTTP_201_CREATED)
async def prompt_retriever(request: schema.RetrieverRequest, db: Session = Depends(get_db)):
    try:

        print(f"Embedding type: {type(request.embedding)}, value: {request.embedding}")

        # Call the function to get textos based on the embedding
        textos = read.get_texts_by_embedding(db, request.embedding)

        # Return the prompt and the textos
        retriever_response = schema.PromptResponse(prompt=request.prompt, text=textos)
        print(retriever_response)
        response_augmenter = post_contexts(retriever_response.model_dump(mode = 'json'))
        print(response_augmenter)
    
    except ValueError as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
