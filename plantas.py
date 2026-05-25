from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime

class Plantas:
    def __init__(self, uri: str = "mongodb+srv://luzzz06:UxVkjeZjqCzeNTFE@luzz.jzuseoq.mongodb.net/?retryWrites=true&w=majority&appName=luzz"):
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
            self.cliente.admin.command('ping')
            
            self.db = self.cliente['plantas']  # Base de datos principal
            self.usuarios = self.db['usuarios'] # Colección de personas
            self.coleccion_plantas = self.db['plantas'] # Colección de las plantas físicas # Referencia clara a la colección de plantas
            
            self.usuarios.create_index("email", unique=True)
            print("✅ Conexión a Atlas Exitosa")
        except ConnectionFailure:
            print("❌ Error: No se pudo conectar a MongoDB Atlas")
            raise
    
    def crear_usuario(self, nombre, email, password):
        try:
            rol_asignado = "administrador" if email == "ubiarcomarialuz@gmail.com" else "usuario"
            resultado = self.usuarios.insert_one({
                "nombre": nombre,
                "email": email,
                "password": password, 
                "rol": rol_asignado,
                "fecha_registro": datetime.now(),
                "activo": True
            })
            return str(resultado.inserted_id)
        except DuplicateKeyError:
            return None
        
    def buscar_usuario(self, email):
        try:
            return self.usuarios.find_one({"email": email})
        except Exception as e:
            print(f"Error: {e}")
            return None

    def actualizar_contrasena(self, email, password_encriptada):
        try:
            resultado = self.usuarios.update_one(
                {"email": email},
                {"$set": {"password": password_encriptada}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            return False