from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional, Dict

# 💡 Eliminamos 'from seguridad import verificar_password' porque ya no usamos ese archivo

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
                "password": password, # Contraseña ya encriptada proveniente de app.py
                "fecha_registro": datetime.now(),
                "activo": True
            })
            return str(resultado.inserted_id)
        except DuplicateKeyError:
            print(f"❌ Error: El email {email} ya existe")
            return None
    
    def obtener_usuario(self, usuario_id: str) -> Optional[Dict]:
        """Obtiene un usuario por su ID convirtiéndolo a string."""
        try:
            usuario = self.usuarios.find_one({"_id": ObjectId(usuario_id)})
            if usuario:
                usuario['_id'] = str(usuario['_id'])
            return usuario
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None

    def buscar_usuario_por_correo(self, email: str) -> Optional[Dict]:
        """Busca si un correo existe en la colección de usuarios."""
        try:
            usuario = self.usuarios.find_one({"email": email})
            if usuario:
                usuario['_id'] = str(usuario['_id'])
                return usuario
            return None
        except Exception as e:
            print(f"Error al buscar usuario por correo: {e}")
            return None

    def actualizar_password(self, email: str, password_encriptada: str) -> bool:
        """Actualiza la contraseña (ya encriptada) de un usuario."""
        try:
            resultado = self.usuarios.update_one(
                {"email": email},
                {"$set": {"password": password_encriptada}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar la contraseña: {e}")
            return False
        
    def obtener_plantas(self):
        return self.db.plantas.find()



if __name__ == "__main__":
    add_plants = Plantas()