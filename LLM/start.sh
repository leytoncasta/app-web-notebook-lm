#!/bin/sh

# Function to check if port is in use
check_port() {
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i:11434 > /dev/null 2>&1; then
            kill $(lsof -t -i:11434)
        fi
    else
        # Fallback if lsof is not available
        if netstat -tuln | grep ":11434" > /dev/null 2>&1; then
            pkill -f ".*:11434.*"
        fi
    fi
}

# Check and kill any existing process
check_port

# Start Ollama service
ollama serve &

# Wait for service to be ready
sleep 10

# Pull the model
ollama pull llama3.2:1b

# Keep the container running
tail -f /dev/null