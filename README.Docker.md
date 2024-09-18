# PROCSTOP 
- PROCSTOP es un chatbot emocional con el objetivo de apoyar a las personas en su momento de debilidad y recomendarles actividades para mejorar su estado de ánimo.
- Se trata de una aplicación web desarrollada principalmente con Flask (Python), MongoDB Atlas, y la API de OpenAI. 
- La aplicación está empaquetada en una imagen Docker para facilitar su ejecución sin necesidad de instalar Python o configurar dependencias adicionales.
## Instrucciones para ejecutar la aplicación Procstop
### Requisitos previos
- Instalar Docker
Si Docker no está instalado en tu sistema, sigue los pasos correspondientes según tu sistema operativo:

- Windows y Mac
- Descarga Docker Desktop desde Docker Desktop Download y sigue las instrucciones de instalación.

- Reinicia tu computadora si es necesario.

- Verifica que Docker esté instalado correctamente abriendo una terminal y ejecutando el siguiente comando:


docker --version
Linux
Sigue esta guía para instalar Docker en tu distribución de Linux: Guía de instalación de Docker en Linux.

- Verifica la instalación con el siguiente comando:

docker --version

- Descargar imagen de Docker Hub
    Si la imagen está disponible en Docker Hub, puedes descargarla directamente ejecutando el siguiente comando:
    docker pull clsk212/procstop_app:latest

- Ejecutar la aplicación
    Una vez que tengas la imagen cargada, puedes seguir estos pasos para ejecutar la aplicación:

    1. Ejecutar el contenedor
        Ejecuta el siguiente comando para iniciar la aplicación:

        docker run -p 5000:5000 procstop_app:latest
        Esto ejecutará la aplicación y la expondrá en el puerto 5000. Para acceder a la aplicación, abre tu navegador y visita la siguiente URL:

        http://localhost:5000

    2. Parar el contenedor
    Para detener la aplicación, puedes hacer lo siguiente:

    Presiona CTRL + C en la terminal donde está ejecutándose el contenedor.