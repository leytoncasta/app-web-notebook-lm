from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aumentador.path import router as augment_router

app = FastAPI(
    title="Augment App",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # embedding url (need to be define)
    allow_credentials=True,
    allow_methods=["POST"],  # Allows just POST method
    allow_headers=["*"],  # Allows all headers
)

app.include_router(augment_router)
