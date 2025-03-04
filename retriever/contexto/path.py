from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
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
@router.post("/contexto", response_model=schema.AugmentResponse, status_code=status.HTTP_201_CREATED)
async def prompt_retriever(request: schema.RetrieverRequest, db: Session = Depends(get_db)):
    try:
        textos = read.get_texts_by_embedding(db, request.embedding)
        retriever_response = schema.PromptResponse(prompt=request.prompt, text=textos)
        logger.info(f"Retriever response: {retriever_response}")
        
        augmented_response = await post_contexts(retriever_response.model_dump(mode='json'))
        logger.info(f"Augmented response: {augmented_response}")

        return augmented_response

    except HTTPException:
        raise

    except ValueError as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )