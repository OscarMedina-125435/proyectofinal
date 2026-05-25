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
            if email == "ubiarcomarialuz@gmail.com":
                rol_asignado = "administrador"
            else:
                rol_asignado = "usuario"

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

    def insertar_planta(self, nombre, especie, estado):
        try:
            resultado = self.db.plantas.insert_one({
                "nombre": nombre,
                "especie": especie,
                "estado": estado,
                "fecha_registro": datetime.now()
            })
            return str(resultado.inserted_id)
        except Exception as e:
            print(f"Error al insertar planta: {e}")
            return None

    def actualizar_planta(self, planta_id, nombre, especie, estado):
        try:
            resultado = self.db.plantas.update_one(
                {"_id": ObjectId(planta_id)},
                {"$set": {"nombre": nombre, "especie": especie, "estado": estado}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar planta: {e}")
            return False

    def eliminar_planta(self, planta_id):
        try:
            resultado = self.db.plantas.delete_one({"_id": ObjectId(planta_id)})
            return resultado.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar planta: {e}")
            return False


if __name__ == "__main__":
    add_plants = Plantas()