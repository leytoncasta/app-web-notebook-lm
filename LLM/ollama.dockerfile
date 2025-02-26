FROM ollama/ollama:latest

# Install lsof
RUN apt-get update && apt-get install -y lsof

COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT ["/start.sh"]