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
### Instalación Python 3.12
Para lanzar la aplicación es necesario tener instalado Python 3.12.
Para comprobar la versión que tenemos instalada podemos ejecutar uno de los siguientes comandos
```
python --version
```
![image](https://github.com/user-attachments/assets/c322f43b-30b4-410a-b8d9-2cd599f23b06)
```
py -0
```
![image](https://github.com/user-attachments/assets/e768f89f-a1d2-4c0b-9c40-d832da782954)

En caso de no tener la versión correcta de Python, ejecuta el siguiente comando para su instalación:
- **Windows**  
```
winget search Python.Python.3.12
```
- **Linux (Ubuntu)**
```
sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
```

### Instalación de librerías
Este proyecto utiliza diferentes librerías lo que implica que el proceso de instalación puede demorarse.
Se pueden seguir dos caminos:
#### Instalación de librerías dentro de un Entorno Virtual venv. (Recomendado)
- **Windows** :
(Asegúrate de estar en la ruta del proyecto)
```
python -m venv nombre_del_entorno
nombre_del_entorno/Scripts/activate
py -m pip install -r .\requirements.txt
```
- **Linux (Ubuntu)**: (Asegúrate de estar en la ruta del proyecto)
```
python3 -m venv nombre_del_entorno
source nombre_del_entorno/bin/activate
py -m pip install -r .\requirements.txt
```

#### Instalación de librerías directamente en tu ordenador.
- **Windows / Linux (Ubuntu)** (Asegúrate de estar en la ruta del proyecto)
```
py -m pip install -r ./requirements.txt
```

## Uso
Una vez se tiene Python 3.12 instalado y las librerías instaladas (en local o en un venv)
el proyecto ya puede ejecutarse.
Para ello únicamente hay que ejecutar el archivo **app.py** y abrir el host:
- **Windows** :
```
python app/app.py
```
- **Linux (Ubuntu)**:
```
python3.12 app/app.py
```
Al ejecutarlo se habilitará, al menos, un puerto local donde se lanzará la web.
Para acceder puedes hacer Control + Click en los enlaces http

![image](https://github.com/user-attachments/assets/fb2a0d35-7dd6-4abd-884f-98153b2c5c32)

o abrir tu navegador predeterminado y escribir en la barra superior localhost (se autocompletará)

![image](https://github.com/user-attachments/assets/4a37e7b2-ef13-4524-9635-5727dca603db)

## Contribución
Si deseas contribuir a este proyecto:pueda
1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-feature`).
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva feature'`).
4. Envía tu rama (`git push origin feature/nueva-feature`).

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
