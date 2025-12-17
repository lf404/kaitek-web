# create_admin.py

from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from config import Config

# Conexión a MongoDB
client = MongoClient(Config.MONGO_URI)

# Base de datos explícita (CLAVE DEL ÉXITO)
db = client[Config.DB_NAME]

# Insertar admin
db.admins.insert_one({
    "username": "admin",
    "password": generate_password_hash("1234")
})

print("Usuario admin creado correctamente")
