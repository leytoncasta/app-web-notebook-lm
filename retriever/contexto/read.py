from sqlalchemy.orm import Session
from sqlalchemy import func
from scipy.spatial.distance import cosine
from . import model
import numpy as np

def get_texts_by_embedding(db: Session, query_embedding: list[float]) -> list[str]:
    # Convert the query vector to a NumPy array
    query_embedding = np.array(query_embedding)

    # Normalize the query vector for cosine similarity
    query_embedding_norm = query_embedding / np.linalg.norm(query_embedding)

     # Convert the normalized NumPy array to a Python list
    query_embedding_list = query_embedding_norm.tolist()

    # Perform the cosine similarity search
    most_similar = (
        db.query(model.FilesDB.id_session)
        .order_by(func.cosine_distance(model.FilesDB.embeddings, query_embedding_list))
        .first()
    )

    if not most_similar:
        raise ValueError("No matching session found.")
    
    # Retrieve the id_session of the most similar vector
    id_session = most_similar.id_session

    # Fetch all texto fields for the id_session
    results = (
        db.query(model.FilesDB.texto)
        .filter(model.FilesDB.id_session == id_session)
        .all()
    )

    # Extract the texto fields
    textos = [result.texto for result in results]
    return textos
