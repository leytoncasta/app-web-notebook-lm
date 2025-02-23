-- Create the new schema
CREATE SCHEMA IF NOT EXISTS vectorial;

-- Set the search path to the new schema (vectorial by default)
SET search_path TO vectorial, public;

-- Create the extension in the new schema
CREATE EXTENSION IF NOT EXISTS vector SCHEMA vectorial;

-- Create the table in the new schema
CREATE TABLE session_embeddings (
    id_session INT NOT NULL,  -- Unique identifier for each session
    embedding vector(1536) NOT NULL  -- Column to store vector embeddings
);
