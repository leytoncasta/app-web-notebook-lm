from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from . import model

def get_texts_by_embedding(db: Session, query_embedding: list[float]) -> list[str]:
    
    vector_str = f"[{','.join(str(x) for x in query_embedding)}]"
    
    query = text("""
        WITH vector_lengths AS (
            SELECT id_session, 
                   vector_dims(embeddings) as vec_length
            FROM vectorial.session_embeddings
        )
        SELECT e.id_session 
        FROM vectorial.session_embeddings e
        INNER JOIN vector_lengths vl ON e.id_session = vl.id_session
        WHERE vl.vec_length = vector_dims((:embedding)::vector)
        ORDER BY e.embeddings <=> (:embedding)::vector
        LIMIT 1
    """)
    
    # Execute with the string representation
    most_similar = db.execute(
        query,
        {"embedding": vector_str}
    ).first()

    if not most_similar:
        raise ValueError(f"No matching sessions found with vector dimension {len(query_embedding)}")
    
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