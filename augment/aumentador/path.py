from fastapi import APIRouter, Depends, status, HTTPException
from service.api import post_searching
from . import schema
import logging

# Define the FastAPI router
router = APIRouter(
    prefix="/augment",
    tags=["aument"]
)

# Set up logging
logger = logging.getLogger(__name__)

# Define the POST method
@router.post("/aumentador", status_code=status.HTTP_201_CREATED)
async def augment_search(request: schema.AugmentRequest):
    try:

        # Log the received string
        logger.info(f"Received string: {request.text}")

        # make searching
        make_searching = post_searching(request.text, request.prompt)
        augment_reponse = schema.AugmentResponse(question=make_searching)
        response_llm = augment_reponse.model_dump(exclude_none=True)
        print(response_llm)
        return response_llm
          
    except ValueError as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

