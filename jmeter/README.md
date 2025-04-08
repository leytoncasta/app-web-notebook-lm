# Pruebas de Carga con Jmeter

## Instalación
Seguir las instrucciones de instalación que se muestran a en el [link](https://jmeter.apache.org/download_jmeter.cgi)

## Ejecución Aplicación
Una vez haya realizado la descarga y posterior a descomprimir el .zip, debemos ir a la carpeta bin y ejecutar el archivo "jmeter.bat"

## Uso
En la interfaz de Jmeter, debemos ir a "File" y "Open". En la ventana de díalogo debemos seleccionar el archivo "CSV Data Set Conffig.jmx" que se encuentra en la carpeta "jmeter" de este repositorio.

## Configuración
Una vez realizado el paso anterior, debemos configuara con la IP externa de la instacia del **Backend**, en el campo "Server Name or IP" de cada unos de los sampler de "HTTP Request". Es decir "userRegistration", "UserLogin", "createChat", "uploasdDocument" y "userPrompt". 

Por último, añadimos la ruta absoluta del archivo "test_usuarios.csv" que se encuentra en la carpeta "jmeter" de este repositorio en el elemento de configuración **Data Pruebas**, sobre el campo *Filename*
