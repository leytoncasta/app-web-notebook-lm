INSERT INTO vectorial.session_embeddings (id_session, texto, embeddings)
VALUES
    (1, 'Text 1', ARRAY[0.1, 0.2, 0.3]::vector),
    (2, 'Text 2', ARRAY[0.4, 0.5, 0.6]::vector);