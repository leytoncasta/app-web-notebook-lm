## app-web-notebook-lm
### Ejecución de los Servicios
Para ejecutar los diferentes servicios en un solo comando, asegúrese de que Docker Desktop (en Windows/macOS) o Docker (en Linux) estén en ejecución.

Luego, ejecute el siguiente comando en la terminal:
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
