#!/bin/bash
set -e

# Esperar a que apt/dpkg estén libres
while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
   echo "Esperando a que apt/dpkg estén disponibles..."
   sleep 3
done

# Instalar Docker y Docker Compose
apt-get update
apt-get install -y docker.io docker-compose

# Instalar gsutil si no está
apt-get install -y google-cloud-sdk

# Autenticación con Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
TOKEN=$(gcloud auth print-access-token)
echo $TOKEN | docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev

# Descargar tu archivo docker-compose desde Cloud Storage
gsutil cp gs://desarrollo-cloud-web-service/docker-compose-web-gcp.yml .

# Levantar servicios
docker-compose -f docker-compose-web-gcp.yml up -d