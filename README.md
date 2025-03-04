## app-web-notebook-lm
### Ejecución de los Servicios
Para ejecutar los diferentes servicios en un solo comando, asegúrese de que Docker Desktop (en Windows/macOS) o Docker (en Linux) estén en ejecución.

Luego, ejecute el siguiente comando en la terminal en el directorio inicial del repositorio:
```
docker-compose up --build -d
```
Este comando se encargará de:

Construir las imágenes necesarias si aún no existen.
Crear y ejecutar los contenedores en segundo plano (-d modo detached).

Si necesita detener los servicios, utilice:
```
docker-compose down
```
Para ver los logs en tiempo real, ejecute:
```
docker-compose logs -f
```
Si se quisiera ejecutar un servicio en especifico se puede utilizar el comando 
```
docker build -f name_fockerfile.dockerfile -t tags_for_the_image . 
```
El punto final (.) indica que el contexto de construcción será el directorio actual. Por lo tanto, asegúrese de ejecutar este comando desde la carpeta correspondiente a uno de los microservicios para garantizar que Docker tenga acceso a los archivos necesarios
