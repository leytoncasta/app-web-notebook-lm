from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aumentador.path import router as augment_router
import uvicorn

app = FastAPI(
    title="Augment App",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://retriever:8080"],  # embedding url (need to be define)
    allow_credentials=True,
    allow_methods=["POST"],  # Allows just POST method
    allow_headers=["*"],  # Allows all headers
)

app.include_router(augment_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2000)
