from fastapi import FastAPI, File, UploadFile
from pypdf import PdfReader
from typing import List

app = FastAPI()

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Divide el texto en fragmentos de tamaño máximo `chunk_size`."""
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...), chunk_size: int = 500):
    """Recibe un PDF, extrae el texto y lo divide en fragmentos."""
    try:
        pdf_reader = PdfReader(file.file)
        text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        
        if not text:
            return {"error": "No se pudo extraer texto del PDF"}

        chunks = chunk_text(text, chunk_size)

        return {"num_chunks": len(chunks), "chunks": chunks}
    except Exception as e:
        return {"error": str(e)}