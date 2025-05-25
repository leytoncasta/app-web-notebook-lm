-- The table to create need to be called: PROMPT_RESPONSE

CREATE TABLE prompt_response (
    id SERIAL PRIMARY KEY,
    message TEXT,
    chat_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    status_code INTEGER NOT NULL
);