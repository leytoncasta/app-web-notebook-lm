-- Install the pgvector Extension in the public Schema
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the vectorial schema if it doesn't already exist:
CREATE SCHEMA IF NOT EXISTS vectorial;

-- Set the search path to the new schema
SET search_path TO vectorial, public;

-- Create the table in the new schema
CREATE TABLE vectorial.session_embeddings (
    index SERIAL PRIMARY KEY,    -- Unique identifier for each row
    id_session INT NOT NULL,  -- Unique identifier for each session
    texto TEXT NOT NULL,         -- Column to store the text of the session
    embeddings vector NOT NULL   -- Column to store vector embeddings
);

-- Insert some example data
INSERT INTO vectorial.session_embeddings (id_session, texto, embeddings)
VALUES
    (1, 'Text 1', ARRAY[0.1, 0.2, 0.3]::vector),
    (1, 'Text 2', ARRAY[0.4, 0.5, 0.6]::vector),
    (1, 'Text 3', ARRAY[0.7, 0.8, 0.9]::vector),
    (3, 'Text 4', ARRAY[0.12, 0.21, 0.323]::vector),
    (4, 'Text 5', ARRAY[0.543, 0.9765, 0.653]::vector),
    (2, 'Text 6', ARRAY[0.89, 0.111, 0.234]::vector);
