from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime

class Plantas:
    def __init__(self, uri: str = "mongodb+srv://luzzz06:UxVkjeZjqCzeNTFE@luzz.jzuseoq.mongodb.net/?retryWrites=true&w=majority&appName=luzz"):
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
            self.cliente.admin.command('ping')
            
            self.db = self.cliente['plantas']
            self.usuarios = self.db['usuarios']
            
            
            self.usuarios.create_index("email", unique=True)
            print("✅ Conexión a Atlas Exitosa - Gestión de Usuarios")
        except ConnectionFailure:
            print("❌ Error: No se pudo conectar a MongoDB Atlas")
            raise
    
    def crear_usuario(self, nombre, email, password):
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
            print(f"❌ El email {email} ya existe")
            return None
    
    def obtener_usuario(self, usuario_id):
        try:
            usuario = self.usuarios.find_one({"_id": ObjectId(usuario_id)})
            if usuario:
                usuario['_id'] = str(usuario['_id'])
            return usuario
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None

    def buscar_usuario(self, email):
        try:
            usuario = self.usuarios.find_one({"email": email})
            if usuario:
                usuario['_id'] = str(usuario['_id'])
                return usuario
            return None
        except Exception as e:
            print(f"Error al buscar usuario por correo: {e}")
            return None

    def actualizar_contrasena(self, email, password_encriptada):
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