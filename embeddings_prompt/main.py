from fastapi import FastAPI, Request, HTTPException, status
from google.cloud import pubsub_v1 # Keep for publisher if needed, not for subscriber client in push
from sentence_transformers import SentenceTransformer
import aiohttp
import asyncio
import json
import base64

# ---------------
# Configuración
# ---------------

PROJECT_ID = "desarrollo-cloud-457900"

API_URL_RETRIEVER = "http://retriever:8004/retriever/contexto"

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------
# Procesamiento del mensaje (ahora dentro del endpoint)
# ---------------

async def process_pushed_message(message_data_dict: dict):
    """
    Processes the actual message content after it's been extracted
    from the Pub/Sub push request.
    """
    print(f"Contenido del mensaje procesado: {message_data_dict}")

    text = message_data_dict.get("text") 
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message format: missing 'text' field"
        )
        return

    embedding = model.encode(text).tolist()

    async with aiohttp.ClientSession() as session:
        json_document = {
            "prompt": text,
            "chat_id": message_data_dict.get("chat_id"),
            "embedding": embedding
        }
        try:
            async with session.post(API_URL_RETRIEVER, json=json_document) as response:
                response_text = await response.text()
                if response.status == 200:
                    print(f"Datos enviados exitosamente a {API_URL_RETRIEVER}")
                else:
                    print(f"Error al enviar datos a {API_URL_RETRIEVER}: {response.status} - {response_text}")
        except aiohttp.ClientError as e:
            print(f"Error de conexión con {API_URL_RETRIEVER}: {e}")

# ---------------
# Endpoint para recibir mensajes de Pub/Sub (Push)
# ---------------

@app.post("/pubsub/push") 
async def pubsub_push_endpoint(request: Request):
    """
    Endpoint que Pub/Sub llamará para enviar mensajes.
    """
    envelope = await request.json()
    print(f"Push request recibido: {envelope}")

    if not envelope or "message" not in envelope:
        print("Solicitud inválida de Pub/Sub: falta 'message'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Pub/Sub message format: missing 'message' field"
        )

    pubsub_message = envelope["message"]

    if "data" not in pubsub_message:
        print("Solicitud inválida de Pub/Sub: falta 'data' en 'message'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Pub/Sub message format: missing 'data' in 'message'"
        )

    try:
        # Los datos del mensaje están codificados en base64
        message_data_bytes = base64.b64decode(pubsub_message["data"])
        message_data_str = message_data_bytes.decode("utf-8")
        message_data_dict = json.loads(message_data_str)
    except Exception as e:
        print(f"Error al decodificar o parsear los datos del mensaje: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot decode or parse Pub/Sub message data: {e}"
        )


    asyncio.create_task(process_pushed_message(message_data_dict))

    return "", status.HTTP_204_NO_CONTENT


# ---------------
# Startup de FastAPI
# ---------------

@app.on_event("startup")
async def startup_event():

    print("Servidor FastAPI iniciado. Esperando mensajes push de Pub/Sub en /pubsub/push...", flush=True)