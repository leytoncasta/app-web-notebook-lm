-- The table to create need to be called: PROMPT_RESPONSE

CREATE TABLE prompt_response (
    message TEXT,
    chat_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    status_code INTEGER NOT NULL
);

CREATE TABLE prompt_response (
    id SERIAL PRIMARY KEY,
    message TEXT,
    chat_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    status_code INTEGER NOT NULL
);