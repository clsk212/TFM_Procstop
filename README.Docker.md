![Cabecera](./assets/nombre.png)

## Descripción
- **PROCSTOP** es un chatbot emocional con el objetivo de apoyar a las personas en su momento de debilidad y recomendarles actividades para mejorar su estado de ánimo.
- Se trata de una aplicación web desarrollada principalmente con **Flask (Python), MongoDB Atlas, y la API de OpenAI**.
- La aplicación está empaquetada en una imagen **Docker** para facilitar su ejecución sin necesidad de instalar Python o configurar dependencias adicionales.

## Índice
- [Descripción](#descripción)
- [Instalación](#instalación)
- [Uso](#uso)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Instalación

### **Instalar Docker**  
Si Docker no está instalado en tu sistema, sigue los pasos correspondientes según tu sistema operativo:

- **Windows y Mac**  
  Descarga Docker Desktop desde el [sitio oficial](https://www.docker.com/products/docker-desktop) y sigue las instrucciones de instalación.

  Verifica que Docker esté instalado correctamente abriendo una terminal y ejecutando el siguiente comando:

  ```bash
  docker --version
  ```

- **Linux**  
  Sigue esta [guía](https://docs.docker.com/engine/install/) para instalar Docker en tu distribución de Linux.

  Verifica la instalación con el siguiente comando:

  ```bash
  docker --version
  ```

### Descargar imagen de Docker Hub
Si la imagen está disponible en Docker Hub, puedes descargarla directamente ejecutando el siguiente comando:

```bash
docker pull clsk212/procstop_app:latest
```

## Uso
Una vez que tengas la imagen cargada, puedes seguir estos pasos para ejecutar la aplicación:

1. **Ejecutar el contenedor**  
   Ejecuta el siguiente comando para iniciar la aplicación:

   ```bash
   docker run -p 5000:5000 clsk212/procstop_app:latest
   ```

   Esto ejecutará la aplicación y la expondrá en el puerto 5000. Para acceder a la aplicación, abre tu navegador y visita la siguiente URL:

   ```
   http://localhost:5000
   ```

## Contribución
Si deseas contribuir a este proyecto:
1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-feature`).
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva feature'`).
4. Envía tu rama (`git push origin feature/nueva-feature`).

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
