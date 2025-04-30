#!/bin/bash

# Instalar Docker y Docker Compose
apt-get update
apt-get install -y docker.io docker-compose

# Instalar gsutil si no está
apt-get install -y google-cloud-sdk

# Crear red y volumen (solo si no existen)
docker network create project_network || true
docker volume create relational_db || true

# Autenticación con Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
TOKEN=$(gcloud auth print-access-token)
echo $TOKEN | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev

# Descargar tu archivo docker-compose desde Cloud Storage
gsutil cp gs://desarrollo-cloud-web-service/docker-compose-worker-gcp.yml .

# Levantar servicios
docker-compose -f docker-compose-worker-gcp.yml up -d