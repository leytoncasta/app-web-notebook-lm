from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from . import model

def get_texts_by_embedding(db: Session, query_embedding: list[float]) -> list[str]:
    
    query = text("""
        SELECT id_session 
        FROM vectorial.session_embeddings 
        ORDER BY embeddings <=> CAST(:query_embedding AS vector)
        LIMIT 1
    """).bindparams(bindparam("query_embedding", type_=ARRAY(FLOAT)))
    
    most_similar = db.execute(query, {"query_embedding": query_embedding}).first()

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
