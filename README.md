# App Web Notebook LM

## Ejecución de los Servicios en GCP

Con el fin de lograr ejecutar los servicios de manera correcta, debemos entender la arquitectura que desplegamos:

## Arquitectura de la Aplicación

### (A) Escalabilidad Capa Web

La arquitectura diseñada para este proyecto en Google Cloud Platform (GCP) se compone de una VPC única que integra cuatro subredes especializadas, garantizando escalabilidad, resiliencia y alto rendimiento. La primera subred (10.109.2.0/27) aloja la instancia worker, encargada de ejecutar microservicios clave para el procesamiento de datos, incluyendo la transformación de documentos, la inserción en una base de datos vectorial (PostgreSQL) mediante Cloud SQL (PaaS) y la comunicación con el modelo Gemini para el análisis avanzado de consultas. La segunda subred (10.108.0.0/26) despliega un grupo de autoescalado con el microservicio de frontend, que gestiona la interfaz de usuario, junto con un microservicio en Cloud Run que maneja solicitudes de autenticación, registro, almacenamiento de documentos en Cloud Storage y la publicación de mensajes en Pub/Sub para su procesamiento por parte de los workers.

La tercera subred (10.0.0.0/26) actúa como capa de proxy, albergando un balanceador de carga que distribuye el tráfico externo hacia las instancias saludables del grupo de autoescalado frontend, mejorando la confiabilidad del sistema. Por su parte, la cuarta subred (10.109.0.0/26) ejecuta en Cloud Run el microservicio de chunking, el cual procesa los mensajes de Pub/Sub para fragmentar el texto antes de su análisis.

La arquitectura se complementa con servicios gestionados de GCP, como un balanceador de carga interno para distribuir tráfico desde el servicio de chunking hacia los workers. Donde se hace uso de Artifact Registry para centralizar imágenes Docker, y Gemini para capacidades avanzadas de NLP. Además, Cloud SQL soporta bases de datos relacionales y vectoriales, mientras que Cloud Storage proporciona almacenamiento seguro para documentos. Esta estructura integrada asegura un flujo eficiente de datos, desde la interacción del usuario hasta el procesamiento y almacenamiento final.

![final](https://github.com/user-attachments/assets/b9cb3255-b706-468e-a2e4-3887d4d1ddb1)


### (B) Escalabilidad en el Backend / Workers

En este proyecto, se priorizó la optimización del rendimiento y la escalabilidad mediante el reemplazo de dos componentes críticos. En primer lugar, se separó el microservicio del frontend y el backend, los cuales inicialmente coexistían en un mismo grupo de instancias con escalamiento lento. Para solucionar esto, se migró el backend a Cloud Run, un servicio que permite una escalabilidad autogestionada por GCP más rápida que la configuración manual y evita que las cargas elevadas afecten el frontend, garantizando así una mejor distribución de recursos y una respuesta ágil ante picos de demanda.

El segundo cambio clave fue la migración del microservicio de chunking, que originalmente se ejecutaba en el mismo grupo de instancias destinado a los workers. Al trasladarlo a Cloud Run, se redujo la carga en las instancias críticas, dejando únicamente tres microservicios esenciales en el grupo de workers para un procesamiento más eficiente. Esta modificación no solo mejoró la escalabilidad del servicio de chunking, sino que también aseguró que las tareas principales de procesamiento no se vieran afectadas por fluctuaciones en la demanda. Ambos ajustes contribuyen a una arquitectura más robusta, flexible y preparada para manejar cargas variables sin comprometer el rendimiento del sistema.

## Replicar la arquitectura de GCP

Si deseamos montar todo desde cero en GCP se deben seguir los siguientes pasos:

##### 1. Imagenes

Con el fin de poder hacer un manejo eficiente de las imagenes en docker, se debe crear en GCP un 'Artifact Registry' donde se van a subir cada una de las imagenes. Para subirlas, se debe de manera local configurar el entorno, y luego haciendo referencia al 'tag' que deseamos subir a la nube realizar los siguientes comandos.

```bash
* gcloud auth activate-service-account --key-file=key.json
* gcloud auth configure-docker us-central1-docker.pkg.dev

* docker build -t <<name>>:latest -f <<name>>/<<name>>.dockerfile ./<<name>>
* docker tag <<name>>:latest us-central1-docker.pkg.dev/desarrollo-web-451923/cloud-images/<<name>>:latest
* docker push us-central1-docker.pkg.dev/desarrollo-web-451923/cloud-images/<<name>>:latest
```

NOTA: Ajustar 'backend' al nombre que se desea subir.
Se deben subir cada una de las imagenes necesarias del proyecto, las cuales se describen en la arquitectura de la aplicación.

##### 2. Cloud SQL

Como se describe en la arquitectura, el proyecto cuenta con dos bases de datos: una vectorial, para el amacenamiento correcto del vectores; y otra relacional, para la información de los usuarios y los chats. Para las bases de datos se usa el servicio Cloud SQL con el motor Postgres. Dentro, se debe definir el usuario por el cual se van a conectar a la base de datos, unicamente por la IP Privada.

Este usuario creado, debe contar con todos los permisos necesarios. Para eso, desde el usuario 'postgres' correr:

```bash
GRANT USAGE ON ALL SEQUENCES IN SCHEMA <<NOMBRE_DEL_ESQUEMA>> TO <<NOMBRE_DEL_USUARIO>>;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA <<NOMBRE_DEL_ESQUEMA>> TO <<NOMBRE_DEL_USUARIO>>;
```

##### 3. Cloud Storage

Además, como NDF usamos Cloud Storage, el cual sigue una creación predeterminada. N

##### 4. Maquinas Virtuales

A priori a cualquier cosa, durante la creación de la maquina virtual dadas las especificaciones necesarias debemos habilitar unos elementos puntuales:

1. Seleccionar la cuenta de 'Service Account' que tenga los siguientes permisos:

   - Artifact Registry Reader
   - Editor
   - Service Usage Admin
   - Read/Write Cloud SQL
   - Read/Write Cloud Filestore

2. Configurar las reglas de firewall con el fin de permitir solo el trafico deseado como se especifica
3. En Security habilitar el API: 'Cloud Platform'.

Esto es necesario para que la maquina permita conectividad, tanto con otras maquinas, como con los diferentes servicios que se van a consumir. Dentro de las maquinas virtuales el proceso general con el cual se pueden correr las imagenes es:

```bash
* sudo apt-get update
* sudo apt-get install -y docker.io docker-compose
* sudo docker network create ___specific______network
* gcloud auth configure-docker us-central1-docker.pkg.dev
* TOKEN=$(gcloud auth print-access-token)
        echo $TOKEN | sudo docker login -u oauth2accesstoken --password-stdin https://us-central1-docker.pkg.dev
```

##### 5. Correr Imagenes dentro de las Maquinas Virtuales

Todos los elementos corren por medio de scrips de arranque y docker compose que se encuentran en la carpeta: gcp. A continuación se detalla para cada elemento:

1. Web Service - Script Arranque

```bash
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
```

2. Web Service - Docker Compose

```bash
services:

  frontend:
    container_name: frontend
    image: us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/frontend:latest
    ports:
      - 80:80
```

3. Worker - Script Arranque

```bash
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
gsutil cp gs://desarrollo-cloud-web-service/docker-compose-worker-gcp.yml .

# Levantar servicios
docker-compose -f docker-compose-worker-gcp.yml up -d
```

4. Worker - Docker Compose

```bash
services:

  embeddings_doc:
    container_name: embeddings_doc
    image: us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/embeddings_doc:latest
    ports:
      - "8002:8002"
    networks:
      - project_network
    restart: always

  embeddings_prompt:
    container_name: embeddings_prompt
    image: us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/embeddings_prompt:latest
    ports:
      - "8003:8003"
    networks:
      - project_network
    restart: always

  retriever:
    container_name: retriever
    image:  us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/retriever:latest
    ports:
      - "8004:8004"
    networks:
      - project_network
    restart: always

  augment:
    container_name: augment
    image: us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/augment:latest
    ports:
      - "8005:8005"
    environment:
      API_KEY: AIzaSyArjlDoowr7cU_8bPpISEZkoUB257xs2Ec
    networks:
      - project_network
    restart: always

networks:
  project_network:
    driver: bridge

volumes:
  embeddings_docs:
    driver: local
  embeddings_prompt:
    driver: local
  retriever:
    driver: local
  augment:
    driver: local
```

### 6. Cloud Run

Tanto para el backend, como para el chunking, se utiliza el siguiente comando con el fin de crear el servicio solicitado:

```
gcloud run deploy backend-service \
  --image=us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/backend:latest \
  --platform=managed \
  --region=northamerica-south1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql+psycopg2://XXX:XXX@XXX:XXX/XXX, CLOUD_STORAGE=XXX-XXX-XXX"
```

De manera manual se debe ajustar las variables de entorno necesarias. Igualmente, se debe ajustar la Sub-Net a la que pertenece con base en lo
descrito en el diagrama de arquitectura. Para saber si quedo bien configurado podemo probar una petición a un endpoint; ejemplo:

```
curl -X POST https://backend-service-XXX.northamerica-south1.run.app/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"nombre_usuario": "XXX", "contraseña": "XXX"}'
```

### Pasos de integración

El proceso de integración inicia con el desacoplamiento de los microservicios de backend y chunking, migrándolos a Cloud Run para mejorar su escalabilidad. El backend se despliega en la misma subred que aloja el frontend, manteniendo una comunicación directa y eficiente entre ambos, mientras que su conexión con la base de datos relacional, Pub/Sub y Cloud Storage no requiere configuraciones adicionales, ya que estos servicios conservan sus mismos endpoints. Por otro lado, el microservicio de chunking, alojado en una subred distinta y en otra región, se integra mediante un balanceador de carga global, que distribuye las tareas procesadas hacia el grupo de instancias de workers en la subred principal, asegurando un reparto equitativo de la carga. Los workers mantienen su comunicación con Pub/Sub, la base de datos vectorial (a través de Cloud SQL) y los servicios de Gemini, sin modificaciones en sus endpoints, lo que garantiza continuidad en el flujo de procesamiento y minimiza impactos en la arquitectura existente. Esta estrategia de integración optimiza el rendimiento, la escalabilidad y la resiliencia del sistema sin introducir complejidades innecesarias.

**Variables de Entorno:**

Se configuraron dos variables clave para garantizar la seguridad y flexibilidad del sistema:

1. DATABASE_URL: Almacena el string de conexión a la base de datos, evitando que credenciales sensibles queden expuestas en el build de la imagen desplegada en Cloud Run. Esto protege la información de los usuarios y facilita la rotación de credenciales sin modificar el código.

2. CLOUD_STORAGE: Contiene el nombre del bucket de Cloud Storage donde se guardan los documentos subidos por los usuarios, evitando referencias directas en el código y reduciendo riesgos de exposición accidental de datos confidenciales.

Ambas variables siguen las mejores prácticas de seguridad, manteniendo la configuración fuera del código fuente y permitiendo una gestión centralizada a través de los servicios gestionados de GCP, lo que mejora tanto la protección de datos como la mantenibilidad del sistema.

## Historias de usuario

### 1. Carga de Documentos

- **Como usuario, quiero subir documentos en formato PDF de máximo 5MB, para que la aplicación pueda analizarlos.**  
  **Criterios:**

  1. El usuario puede subir archivos en formato PDF de 5MB.

- **Como usuario, quiero que antes de realizar preguntas al LLM en el chat, se exija que este subido un documento.**  
  **Criterios:**

  1. La aplicación bloquea la funcionalidad de preguntas si no hay un documento cargado.
  2. Se muestra un mensaje indicando que se debe subir un documento antes de realizar preguntas.

- **Como usuario, quiero recibir un mensaje en el chat cuando mi documento se haya procesado correctamente, para saber cuándo puedo revisarlo.**  
  **Criterios:**

  1. Se muestra un mensaje en el chat cuando el documento ha sido procesado exitosamente.
  2. Si ocurre un error en el procesamiento, se notifica al usuario.

- **Como usuario, quiero poder revisar un solo documento en cada chat que tenga.**  
  **Criterios:**
  1. Cada chat está asociado a un único documento.
  2. No es posible subir más de un documento por chat.

### 2. Procesamiento de Texto con IA

- **Como usuario, quiero hacer preguntas sobre el contenido de un documento y recibir respuestas precisas, para aclarar dudas de manera eficiente.**  
  **Criterios:**
  1. El usuario puede realizar preguntas sobre el documento cargado.
  2. La IA responde utilizando la información del documento.

### 3. Interfaz Web y API

- **Como usuario, quiero acceder a la aplicación desde una interfaz web, para gestionar mis chats.**  
  **Criterios:**
  1. La aplicación es accesible desde un navegador web.
  2. El usuario puede iniciar sesión y ver sus chats en la interfaz.

### 4. Gestión de Usuarios y Sesiones

- **Como usuario, quiero registrarme e iniciar sesión en la aplicación, lo cual me permita acceder a los chats.**  
  **Criterios:**

  1. El usuario puede registrarse con un usuario y contraseña.
  2. El sistema valida las credenciales al iniciar sesión.

- **Como usuario, quiero cerrar sesión en cualquier momento, para proteger mi privacidad.**  
  **Criterios:**

  1. Se proporciona un botón de "Cerrar sesión".

- **Como usuario, quiero ver mis chats, para consultar información de diferentes documentos.**  
  **Criterios:**

  1. Se muestra una lista de chats activos en la interfaz.
  2. Cada chat al que le puedo preguntar está asociado a un documento.

- **Como usuario, quiero poder crear tantos chats como yo considere necesarios.**  
  **Criterios:**

  1. No hay un límite en la cantidad de chats que el usuario puede crear.

- **Como usuario, quiero poder consultar las respuesta y preguntas realizada de los chats mientras tenga abierta la sesión (sin persistencia).**  
  **Criterios:**

  1. Las preguntas y respuestas permanecen visibles mientras la sesión esté activa.

- **Como usuario, quiero poder borrar los chats que considere que ya cumplieron su función de consulta.**  
  **Criterios:**
  1. Se proporciona una opción para eliminar chats individualmente.

### 5. Despliegue y Escalabilidad

- **Como administrador, quiero que la aplicación se ejecute en contenedores con Docker y Docker Compose, para facilitar el despliegue y la escalabilidad.**  
  **Criterios:**
  1. La aplicación se ejecuta en un contenedores Docker.
  2. Se proporciona un archivo docker-compose.yml para la orquestación de los servicios.

## Arquitectura de la Aplicación

La arquitectura de la aplicación está compuesta por 10 servicios, descritos a continuación:

1. **Frontend:** Es la capa de experiencia de usuario que gestiona la interacción del cliente con la interfaz gráfica. Permite acciones como iniciar sesión, registrarse y utilizar un chat interactivo, mediante el cual los usuarios pueden cargar documentos y realizar búsquedas específicas de información utilizando un modelo de inteligencia artificial.

2. **Embedding (1 y 2):** Esta capa genera los embeddings, convirtiendo el texto en vectores y llama a los servicios correspondientes una vez ya tenga los resultados convertidos en vectores.

   - **Embedding 1:** Produce embeddings de los chunks y los almacena en la base de datos vectorial.
   - **Embedding 2:** Convierte las preguntas en vectores y los envía al retriever para su procesamiento.
   - **Todos los vectores son de un tamaño fijo, igual 384 posiciones.**

3. **Chunking:** Este servicio divide el texto en chunks o fragmentos, estructurando la información antes de enviarla a Embedding 1 para generar embeddings y almacenarlos en la base de datos vectorial.

4. **Base de datos relacional:** Asegura la persistencia de la información del cliente, como los datos de registro y sus chats asociados.

5. **Base de datos vectorial:** Se encarga de almacenar los documentos cargados por los usuarios, el ID del chat, los embeddings y el texto asociado a cada vector.

6. **Retriever:** Realiza una similitud de coseno entre el prompt (consulta del cliente) y los textos almacenados durante la sesión (un solo chat especifico), devolviendo los fragmentos del documento que mejor se ajusta a la pregunta formulada.

7. **Augment:** Estructura la consulta que se enviará al modelo, recibe la respuesta del modelo y la remite, junto con la consulta original, al servicio del backend directamente.

8. **Backend:** Actúa como orquestador, conectando el frontend con las capas de datos y procesos, y asegurando la comunicación entre los servicios.

El flujo de la aplicación es el siguiente: un usuario inicia sesión en el frontend, abre un chat y, antes de poder realizar preguntas, debe subir un documento. Una vez cargado, el documento es dividido en fragmentos (chunking), procesado para generar sus embeddings y almacenado en la base de datos junto con el ID del chat. Finalmente, el usuario puede comenzar a hacer consultas.

Por otro lado, cuando el usuario realiza una consulta, la pregunta se envía al backend, donde es procesada y vectorizada mediante el servicio de embeddings. Una vez generado el vector, este se utiliza para buscar información relevante en el retriever, identificando los chunks mas relevantes con respecto a la pregunta. Luego, el contexto recuperado y la pregunta se combinan en el módulo de augmentation, que los envía al modelo de lenguaje (Gemini). El LLM genera una respuesta, la cual es devuelta al módulo de augmentation y finalmente con esto se tiene la respuesta para el front end.

## Limitaciones de la aplicación

- Los chat soportan más de un documento, pero está actualmente limitado a uno solo en la interfaz web.
- El tipo de documento debe ser PDF de máximo 5 MB.
- No se persiste el historial de chats una vez se cierra la interfaz web, se cierra o expira la sesión.

## Conclusiones de pruebas de carga

Con respecto a lo que concierne a esta arquitectura, esta es mucho más robusta que la anterior, siendo capaz de soportar cargar más grandes, pero esto tiene el costo de aumentar de forma considerable las latencias, también podemos ver que la arquitectura gracias a las colas del pub sub es más robusta, y permite manejar mejor las cargas sin colapsar el sistema, tal vez por otro lado se pueda aumentar el número de mensajes que procesa cada worker en los prompts.

# UML de la Aplicación

Este diagrama UML representa un modelo de clases simplificado que describe la relación
entre las entidades Usuario, Chat y Documento que interactúan para formar una estructura
de gestión de chats y archivos. La clase Usuario incluye atributos como un identificador
único, nombre de usuario y contraseña, junto con métodos para validar y gestionar
contraseñas, lo que refleja un enfoque en la seguridad y autenticación. Los usuarios tienen
una relación uno a muchos con la clase Chat, indicando que un usuario puede crear
múltiples chats, cada uno identificado por un ID único y vinculado al usuario
correspondiente. A su vez, la clase Documento está asociada a los chats, almacenando
información como el nombre del archivo, el ID del chat al que pertenece y una lista de
fragmentos (chunking). En conjunto, el diagrama representa un modelo para un sistema de
mensajería donde los usuarios interactúan mediante chats con capacidad de carga de
documentos.

```mermaid
classDiagram
    Usuario "1" -- "*" Chat : crea
    Usuario "1" -- "*" Documento : sube
    Chat "1" -- "*" Documento : contiene

    class Usuario {
        +Integer id
        +String nombre_usuario
        +String contraseña
        +validate_password(password)
        +set_password(password)
        +check_password(password)
    }

    class Chat {
        +Integer id
        +Integer id_usuario
    }

    class Documento {
        +Integer id
        +String nombre_archivo
        +Integer chat_id
        +List chunking
    }

```

## Diagram de Componentes

![image](https://github.com/user-attachments/assets/93e7a688-58ac-4ec7-a05a-0631fd29105c)
