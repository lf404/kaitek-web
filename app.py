import os
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_mail import Mail # Importar extensión de correo

# Cargar variables de entorno (.env)
load_dotenv()

from config import Config
from routes.admin import admin_bp
from routes.productos import productos_bp
from routes.catalogo import catalogo_bp

def create_app():
    # Inicializar Flask
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- VERIFICACIÓN DE CONFIGURACIÓN ---
    if not Config.MONGO_URI or not Config.DB_NAME:
        raise ValueError("ERROR: Faltan MONGO_URI o DB_NAME en config.py")

    # --- CONEXIÓN A MONGODB ---
    try:
        client = MongoClient(Config.MONGO_URI)
        app.db = client[Config.DB_NAME]
        client.admin.command('ping')
        print("Conexión a MongoDB exitosa")
    except Exception as e:
        print(f"Error fatal conectando a MongoDB: {e}")
        return None
   
    # --- INICIALIZAR CORREO ---
    # Esto permite enviar emails desde cualquier parte de la app
    mail = Mail(app)
    app.mail = mail

    # --- SISTEMA DE ARCHIVOS ---
    upload_path = os.path.join(Config.UPLOAD_FOLDER, "productos")
    if not os.path.exists(upload_path):
        os.makedirs(upload_path, exist_ok=True)
        print(f"Carpeta de uploads verificada: {upload_path}")

    # --- REGISTRO DE RUTAS ---
    app.register_blueprint(catalogo_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(productos_bp)

    return app

app = create_app()

if __name__ == "__main__":
    if app:
        print("Servidor iniciando...")
        app.run(debug=True)
    else:
        print("La aplicación no pudo iniciar.")