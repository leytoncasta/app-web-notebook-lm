FROM ollama/ollama:latest

# Install lsof
RUN apt-get update && apt-get install -y lsof dos2unix

# Copy and fix the start script
COPY start.sh /start.sh
RUN dos2unix /start.sh && \
    chmod +x /start.sh

ENTRYPOINT ["/start.sh"]