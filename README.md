Instrucciones para ejecutar la aplicación Procstop
Esta es una aplicación web desarrollada con Flask, MongoDB Atlas, y la API de OpenAI. La aplicación está empaquetada en una imagen Docker para facilitar su ejecución sin necesidad de instalar Python o configurar dependencias adicionales.

Requisitos previos
Instalar Docker
Si Docker no está instalado en tu sistema, sigue los pasos correspondientes según tu sistema operativo:

Windows y Mac
Descarga Docker Desktop desde Docker Desktop Download y sigue las instrucciones de instalación.

Reinicia tu computadora si es necesario.

Verifica que Docker esté instalado correctamente abriendo una terminal y ejecutando el siguiente comando:

bash
Copiar código
docker --version
Linux
Sigue esta guía para instalar Docker en tu distribución de Linux: Guía de instalación de Docker en Linux.

Verifica la instalación con el siguiente comando:

bash
Copiar código
docker --version
Descargar la imagen Docker
Tienes dos opciones para obtener la imagen Docker de la aplicación Procstop.

Opción 1: Desde un archivo .tar (si se proporciona)
Descargar el archivo de la imagen: Descarga el archivo procstop_app.tar desde el enlace proporcionado.

Cargar la imagen en Docker: Una vez descargado el archivo, abre una terminal y ejecuta el siguiente comando para cargar la imagen en Docker:

bash
Copiar código
docker load -i procstop_app.tar
Opción 2: Descargar desde Docker Hub
Si la imagen está disponible en Docker Hub, puedes descargarla directamente ejecutando el siguiente comando (reemplaza <tu_usuario> por el nombre de usuario de Docker del autor):

bash
Copiar código
docker pull <tu_usuario>/procstop_app:latest
Ejecutar la aplicación
Una vez que tengas la imagen cargada, puedes seguir estos pasos para ejecutar la aplicación:

1. Ejecutar el contenedor
Ejecuta el siguiente comando para iniciar la aplicación:

bash
Copiar código
docker run -p 5000:5000 procstop_app:latest
Esto ejecutará la aplicación y la expondrá en el puerto 5000. Para acceder a la aplicación, abre tu navegador y visita la siguiente URL:

arduino
Copiar código
http://localhost:5000
2. Parar el contenedor
Para detener la aplicación, puedes hacer lo siguiente:

Presiona CTRL + C en la terminal donde está ejecutándose el contenedor.

Si prefieres detener el contenedor en segundo plano, usa el siguiente comando para listar los contenedores en ejecución:

bash
Copiar código
docker ps
Y luego, para detener el contenedor, ejecuta el siguiente comando, reemplazando <CONTAINER_ID> por el ID del contenedor en ejecución:

bash
Copiar código
docker stop <CONTAINER_ID>
