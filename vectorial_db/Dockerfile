# Use the official PostgreSQL image from the Docker Hub
FROM postgres:15

# Copy the initialization script to create the extension
COPY ./sql/init.sql /docker-entrypoint-initdb.d/init.sql
COPY ./postgresql.conf /etc/postgresql/postgresql.conf

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
    && make install \
    && rm -rf /tmp/pgvector

# Set environment variables for PostgreSQL
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_PORT=${POSTGRES_PORT}

# Expose the PostgreSQL port
EXPOSE 532

# Start PostgreSQL with custom configuration
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
