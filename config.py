import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_por_defecto')
    MONGO_URI = os.environ.get('MONGO_URI')
    DB_NAME = "kaitek_db"
    
    # Directorio base (ya no usaremos uploads locales, pero lo dejamos por si acaso)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    
    # Configuración de Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    
    # Configuración de Correo
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') 
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_RECIPIENT = 'kaitek@ktschile.com'