from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional, Dict

class Plantas:
    def __init__(self, uri: str = "mongodb+srv://luzzz06:UxVkjeZjqCzeNTFE@luzz.jzuseoq.mongodb.net/?retryWrites=true&w=majority&appName=luzz"):
        """Inicializar conexión a MongoDB Atlas para gestión de usuarios"""
        try:
            # Conexión directa ignorando errores de certificados SSL en Windows
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
            self.cliente.admin.command('ping')
            
            self.db = self.cliente['plantas']
            self.usuarios = self.db['usuarios']
            
            # Crear índice único para que no se repitan correos
            self.usuarios.create_index("email", unique=True)
            print("✅ Conexión a Atlas Exitosa - Gestión de Usuarios")
        except ConnectionFailure:
            print("❌ Error: No se pudo conectar a MongoDB Atlas")
            raise
    
    def crear_usuario(self, nombre: str, email: str, password: str) -> Optional[str]:
        """Insertar un nuevo usuario en la base de datos"""
        try:
            resultado = self.usuarios.insert_one({
                "nombre": nombre,
                "email": email,
                "password": password,
                "fecha_registro": datetime.now(),
                "activo": True
            })
            return str(resultado.inserted_id)
        except DuplicateKeyError:
            print(f"❌ Error: El email {email} ya existe")
            return None
    
    def obtener_usuario(self, usuario_id: str) -> Optional[Dict]:
        """Buscar un usuario por su ID"""
        try:
            usuario = self.usuarios.find_one({"_id": ObjectId(usuario_id)})
            if usuario:
                usuario['_id'] = str(usuario['_id'])
            return usuario
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None

    def verificar_login(self, email, password):
        """Validar credenciales para el inicio de sesión"""
        usuario = self.usuarios.find_one({"email": email, "password": password})
        if usuario:
            usuario['_id'] = str(usuario['_id'])
            return usuario
        return None

if __name__ == "__main__":
    add_plants = Plantas()