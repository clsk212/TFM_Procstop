from flask import Flask
from flask_pymongo import PyMongo

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/procstop"
mongo = PyMongo(app)

# Importación de módulos locales
from .user import routes

# Registra los blueprints o rutas si los tienes
# Si routes.py tiene un blueprint, lo registras aquí
# app.register_blueprint(routes.module_blueprint)
