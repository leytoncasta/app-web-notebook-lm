from sqlalchemy.orm import Session
from sqlalchemy import text
from . import model

def get_texts_by_embedding(db: Session, query_embedding: list[float], chat_id: int) -> list[str]:
    vector_str = f"[{','.join(str(x) for x in query_embedding)}]"
    
    query = text("""
        SELECT index, embeddings <=> (:embedding)::vector as similarity_score
        FROM vectorial.session_embeddings
        WHERE id_session = :chat_id
        ORDER BY embeddings <=> (:embedding)::vector
        LIMIT 5
    """)
    
    # Execute with the string representation
    most_similar_vectors = db.execute(
        query,
        {
            "embedding": vector_str,
            "chat_id": chat_id
        }
    ).fetchall()

    if not most_similar_vectors:
        raise ValueError(f"No matching vectors found for chat_id {chat_id}")
    
    # Get the indexes of the most similar vectors
    vector_indexes = [vector.index for vector in most_similar_vectors]

    # Fetch the texto fields for all matching indexes
    results = (
        db.query(model.FilesDB.texto)
        .filter(model.FilesDB.index.in_(vector_indexes))
        .all()
    )

    # Extract the texto fields
    textos = [result.texto for result in results]
    return textos