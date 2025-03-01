-- Install the pgvector Extension in the public Schema
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the vectorial schema if it doesn't already exist:
CREATE SCHEMA IF NOT EXISTS vectorial;

-- Set the search path to the new schema
SET search_path TO vectorial, public;

-- Create the table in the new schema
CREATE TABLE vectorial.session_embeddings (
    id_session INT PRIMARY KEY,  -- Unique identifier for each session
    texto TEXT NOT NULL,         -- Column to store the text of the session
    embeddings vector NOT NULL   -- Column to store vector embeddings
);

-- Insert some example data
INSERT INTO vectorial.session_embeddings (id_session, texto, embeddings)
VALUES
    (1, 'Text 1', ARRAY[0.1, 0.2, 0.3]::vector),
    (2, 'Text 2', ARRAY[0.4, 0.5, 0.6]::vector);
