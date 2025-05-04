# App Web Notebook LM

## Ejecución de los Servicios en GCP

Con el fin de lograr ejecutar los servicios de manera correcta, debemos entender la arquitectura que desplegamos:

Arquitectura de la Aplicación

(A) Escalabilidad Capa Web

La arquitectura diseñada para la capa web en Google Cloud Platform (GCP) está
compuesta por una VPC única que alberga tres subredes especializadas, cada una
con funciones específicas para garantizar escalabilidad, resiliencia y alto
desempeño.

La primera subred (10.109.1.32/27) está dedicada a la instancia worker, que ejecuta
microservicios clave para el procesamiento de datos. Estos microservicios se
encargan de leer y transformar los documentos cargados por los usuarios, insertar
la información en una base de datos vectorial (PostgreSQL) administrada mediante
Cloud SQL (PaaS), y comunicarse con el modelo Gemini para el procesamiento
avanzado de consultas. Esta instancia actúa como el núcleo de procesamiento de la
arquitectura, asegurando que los datos sean correctamente estructurados y
almacenados para su posterior recuperación.

En la segunda subred (10.109.1.0/27), se despliega un grupo de autoescalado
(instance group) que aloja los microservicios del frontend y backend (web-server).
Este grupo gestiona las solicitudes de los usuarios, autenticándolas mediante una
base de datos relacional y redirigiéndolas a la instancia worker para su
procesamiento. Además, se encarga de almacenar los documentos en Cloud
Storage y coordinar el flujo de chats y archivos hacia los workers. Para manejar
cargas variables, el grupo emplea una política de autoescalado que inicia con una
sola instancia y escala hasta tres cuando el uso de CPU supera el 60%, optimizando
así el rendimiento y la disponibilidad del servicio.

La tercera subred (10.0.0.0/26) funciona como capa de proxy y alberga un
balanceador de carga, que es el punto de entrada principal para las solicitudes
externas. Este componente verifica constantemente el estado de las instancias en
el grupo de autoescalado y distribuye el tráfico únicamente hacia aquellas que están
activas y saludables, mejorando la confiabilidad del sistema.

La arquitectura se complementa con servicios administrados de GCP que potencian
su funcionalidad. El Artifact Registry centraliza las imágenes Docker utilizadas en los
despliegues, agilizando la gestión de contenedores. Por otro lado, Gemini
proporciona capacidades avanzadas de procesamiento de lenguaje natural (NLP),
mientras que Cloud SQL soporta tanto la base de datos relacional para
autenticación como la base de datos vectorial para búsquedas semánticas.
Finalmente, Cloud Storage ofrece un almacenamiento seguro y escalable para los
documentos subidos por los usuarios. La Figura 1 representa la arquitectura descrita.

AAAAAAAAAAAAAAAAAAAAAAAAAAA

Escalabilidad en el Backend (workers)

Como parte de la evolución del proyecto y para establecer un punto de comparación
en las pruebas de rendimiento, se implementaron cambios significativos sobre la
arquitectura inicial de escalabilidad de la capa web. Estas modificaciones buscan
mejorar la capacidad de procesamiento y distribuir eficientemente la carga de
trabajo.

El primer cambio fundamental fue la migración de la infraestructura de workers a una
nueva subred (10.109.2.0/27) en la región us-east5. Esta decisión se tomó debido a
limitaciones en el número de instancias permitidas en la subred original
(10.109.1.32/27) de la región us-west1. La nueva configuración implementa un grupo
de instancias autoescalables (instance group) para los workers, similar al utilizado
en el web-server de la arquitectura inicial. Este grupo aplica la misma política de
autoescalado, expandiéndose cuando la utilización de CPU supera el 60%, lo que
proporciona mayor capacidad operativa y resiliencia durante picos de demanda.

Como segunda mejora, se incorporó el servicio Pub/Sub de GCP, que actúa como
sistema de colas y balanceador de carga inteligente entre la capa web
(frontend/backend) y la capa de procesamiento (workers). Esta solución ofrece
múltiples ventajas:

1. Funciona como buffer para las solicitudes, evitando la sobrecarga de los
   microservicios.
2. Garantiza la persistencia de las peticiones incluso durante escalamientos o
   fallos temporales.
3. Distribuye automáticamente la carga entre los workers disponibles
4. Permite comunicación bidireccional eficiente entre componentes

La implementación de Pub/Sub no solo optimiza el flujo de trabajo, sino que también
desacopla los componentes del sistema, mejorando la mantenibilidad y
permitiendo un escalamiento independiente de cada capa. Esta arquitectura
revisada proporciona una base más robusta para manejar cargas variables y
mantiene la coherencia con los servicios gestionados de GCP utilizados en el diseño
original. La Figura 2 muestra el cambio descrito.

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

### Replicar la arquitectura de GCP

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
    depends_on:
      - backend
    networks:
      - project_network

  backend:
    container_name: backend
    image: us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/backend:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg2://postgres:admin@10.189.176.3:5432/USER # IP del SQL en GCP
      CLOUD_STORAGE: bucket-documents-users
    networks:
      - project_network
    restart: always

networks:
  project_network:
    driver: bridge
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

  chunking:
    image: us-central1-docker.pkg.dev/desarrollo-cloud-457900/desarrollo-cloud/chunking:latest
    container_name: chunking
    ports:
      - "8001:8001"
    environment:
      CLOUD_STORAGE: bucket-documents-users
    networks:
      - project_network
    restart: always

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
  chunking:
    driver: local
  embeddings_docs:
    driver: local
  embeddings_prompt:
    driver: local
  retriever:
    driver: local
  augment:
    driver: local
```

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

9. **Ollama:** Procesa las búsquedas solicitadas por el cliente en los documentos y proporciona una respuesta que se envía al servicio de Augment.

El flujo de la aplicación es el siguiente: un usuario inicia sesión en el frontend, abre un chat y, antes de poder realizar preguntas, debe subir un documento. Una vez cargado, el documento es dividido en fragmentos (chunking), procesado para generar sus embeddings y almacenado en la base de datos junto con el ID del chat. Finalmente, el usuario puede comenzar a hacer consultas.

Por otro lado, cuando el usuario realiza una consulta, la pregunta se envía al backend, donde es procesada y vectorizada mediante el servicio de embeddings. Una vez generado el vector, este se utiliza para buscar información relevante en el retriever, identificando los chunks mas relevantes con respecto a la pregunta. Luego, el contexto recuperado y la pregunta se combinan en el módulo de augmentation, que los envía al modelo de lenguaje (Gemini). El LLM genera una respuesta, la cual es devuelta al módulo de augmentation y finalmente con esto se tiene la respuesta para el front end.

## Limitaciones de la aplicación

- Los chat soportan más de un documento, pero está actualmente limitado a uno solo en la interfaz web.
- El tipo de documento debe ser PDF de máximo 5 MB.
- No se persiste el historial de chats una vez se cierra la interfaz web, se cierra o expira la sesión.

## Conclusiones de pruebas de carga

Durante el proceso de pruebas de carga, se identificó un rendimiento sustancial en los
microservicios que conforman la aplicación. En comparación con la entrega anterior, se
observó una mejora significativa en los servicios de la capa web-server, especialmente en
la Arquitectura A (escalabilidad de la capa web-server). Mientras que en la segunda entrega
el sistema alcanzaba su límite con aproximadamente 70 usuarios, en esta arquitectura, se
alcanzó un umbral de 257 usuarios interactuando con la ruta crítica (desde el login hasta la
carga del documento) antes de que se presentara degradación. Las pruebas se realizaron
con 300 usuarios en 240 segundos, lo que permitió concluir que el balanceo de carga y las
políticas de autoescalado fueron clave para evitar un colapso prematuro del sistema.
Además, se logró atender entre 3 y 6 clientes simultáneamente en ciertos intervalos de
tiempo, demostrando una capacidad de respuesta eficiente.

Por su parte, la Arquitectura B (escalado de la capa de proceso) mostró un rendimiento aún
más destacado. Las pruebas se ejecutaron con 600 usuarios en 240 segundos, de los
cuales 397 completaron exitosamente la ruta crítica 1, casi el doble que en la Arquitectura
A. Además, se observó una atención recurrente de 8 a 12 clientes simultáneos en
determinados periodos, lo que confirma una mayor capacidad de procesamiento.  
Un hallazgo relevante fue que la capa de proceso (workers) en ambas arquitecturas no
experimentó sobrecarga, permitiendo manejar la demanda de clientes que completaron la
ruta crítica (257 en la Arquitectura A y 397 en la B). Esto indica que el cuello de botella se
encontraba en la capa web-server, ya que los workers nunca alcanzaron su límite de
capacidad. Los picos máximos de CPU en esta capa fueron del 38.96% (Arquitectura A) y
197% (Arquitectura B), muy por debajo del máximo teórico del 300%.

Al igual que en la entrega anterior, los servicios administrados (Cloud SQL y Cloud Storage)
demostraron alta disponibilidad y adaptabilidad ante el incremento de demanda, sin
convertirse en puntos únicos de fallo.

Los resultados evidencian que las nuevas arquitecturas marcaron un hito en las pruebas de
carga, logrando una mejora superior al 200% en rendimiento. Este avance se atribuye
directamente a las estrategias de escalabilidad implementadas, consolidando un sistema
más robusto y eficiente.

## Consideraciones adicionales

La implementación del balanceador de carga combinado con Pub/Sub como sistema de
colas demostró ser estratégicamente acertada, evidenciándose una mejora sustancial en
la capacidad del sistema. Esta arquitectura permitió manejar un mayor volumen de
solicitudes concurrentes y soportar un crecimiento significativo de usuarios recurrentes sin
comprometer la estabilidad del servicio.

Sin embargo, durante las pruebas de carga identificamos una limitación crítica en el
mecanismo de escalamiento actual. Los grupos de instancias presentan una latencia
considerable en su respuesta a picos de demanda, debido principalmente al tiempo
requerido para el aprovisionamiento y la inicialización de nuevas instancias (incluyendo el
arranque de los microservicios). Para mitigar este problema, proponemos dos estrategias
complementarias:

1. Optimización del autoescalado tradicional:
   • Mantener instancias reservadas desde el inicio (aunque pueda generar cierta
   subutilización de recursos)
   • Ajustar los umbrales de escalado a valores más conservadores (40%-50% de uso
   de CPU)
   • Esto proporciona un margen temporal suficiente para que nuevas instancias
   estén operativas antes de alcanzar puntos críticos de carga

2. Migración a arquitectura basada en contenedores:
   Evaluar el uso de servicios como Cloud Run o Kubernetes (GKE)
   • Escalamiento horizontal más rápido (en cuestión de segundos)
   • Mayor eficiencia en la gestión de recursos
   • Simplificación del ciclo de vida de las aplicaciones
   • Mejor mantenibilidad y despliegues continuos

La solución con contenedores representa un enfoque más moderno y elástico,
particularmente adecuado para cargas de trabajo variables.

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

