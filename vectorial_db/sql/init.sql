-- Create the new schema
CREATE SCHEMA IF NOT EXISTS vectorial;

-- Set the search path to the new schema (vectorial by default)
SET search_path TO vectorial, public;

-- Install the vector extension in the new schema
CREATE EXTENSION IF NOT EXISTS vector SCHEMA vectorial;

-- Create the table in the new schema
CREATE TABLE vectorial.session_embeddings (
    id_session INT PRIMARY KEY,  -- Unique identifier for each session
    texto TEXT NOT NULL,      -- Column to store the text of the session
    embeddings vector NOT NULL  -- Column to store vector embeddings
);
