
# -----------------------------------------------------------------------------
# Imagen Base
# -----------------------------------------------------------------------------
FROM node:18-alpine

# -----------------------------------------------------------------------------
# Configuración del Directorio de Trabajo
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# Instalación de Dependencias
# -----------------------------------------------------------------------------
# Copiar package.json primero para mejor caché
COPY package.json .

# Instalar dependencias
RUN npm install

# Instalar serve globalmente para servidor de producción
RUN npm i -g serve

# -----------------------------------------------------------------------------
# Construcción de la Aplicación
# -----------------------------------------------------------------------------
# Copiar código fuente
COPY . .

# Construir la aplicación
RUN npm run build

# -----------------------------------------------------------------------------
# Configuración del Servidor
# -----------------------------------------------------------------------------
# Exponer puerto 3000
EXPOSE 3000

# Iniciar servidor de producción
CMD [ "serve", "-s", "dist" ]