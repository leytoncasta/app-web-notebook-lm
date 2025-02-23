# Use the official PostgreSQL image from the Docker Hub
FROM postgres:15

# Install pgvector extension
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-server-dev-15 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone and install pgvector
RUN git clone https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    && make \
    && make install

# Copy the initialization script to create the extension
# COPY init.sql /docker-entrypoint-initdb.d/

# Set environment variables for PostgreSQL
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Expose the PostgreSQL port
EXPOSE 5432
