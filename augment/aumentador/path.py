from fastapi import APIRouter, status, HTTPException
from service.api import post_searching
from . import schema
from .question import structure_question
import logging

# Define the FastAPI router
router = APIRouter(
    prefix="/augment",
    tags=["augment"]
)

# Set up logging
logger = logging.getLogger(__name__)

# Define the POST method
@router.post("/", response_model=schema.AugmentResponse, status_code=status.HTTP_201_CREATED)
async def augment_search(request: schema.AugmentRequest):
    logger.info(f"Received request: {request}")
    try:
        # make question
        model = "llama3.2:1b"
        prompt = structure_question(request.text, request.prompt)
        stream = False
        context = []

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "context": context
        }
        
        llm_response = await post_searching(payload)
        
        # Create properly formatted response
        augment_response = schema.AugmentResponse(
            model=model,
            prompt=prompt,
            stream=stream,
            context=[str(c) for c in llm_response.get('context', [])],
            response=llm_response.get('response', ''),
            done=llm_response.get('done', False),
            done_reason=llm_response.get('done_reason', '')
        )
        
        return augment_response
          
    except ValueError as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

