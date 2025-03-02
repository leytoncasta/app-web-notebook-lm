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
@router.post("/",response_model=schema.AugmentResponse , status_code=status.HTTP_201_CREATED)
async def augment_search(request: schema.AugmentRequest):
    try:

        # Log the received string
        logger.info(f"Received string: {request.text}")

        # make question
        model = "llama3.2:1b"
        prompt = structure_question(request.text, request.prompt)
        stream = False
        context = []
        #pregunta = "Basado en este texto: " + request.text + " Responde a la siguiente pregunta: " + request.prompt

        # make searching
        augment_reponse = schema.AugmentResponse(model=model, prompt=prompt, stream=stream, context=context)
        print(augment_reponse)
        response_llm = post_searching(augment_reponse.model_dump(exclude_none=True))
        print(response_llm)
          
    except ValueError as e:
        # Handle errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

