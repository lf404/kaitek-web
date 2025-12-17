import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_por_defecto')
    MONGO_URI = os.environ.get('MONGO_URI')
    DB_NAME = "kaitek_db"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') 
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_RECIPIENT = 'kaitek@ktschile.com'