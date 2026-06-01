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
            self.coleccion_plantas = self.db['plantas'] 
            
            self.usuarios.create_index("email", unique=True)
            print("✅ Conexión a Atlas Exitosa")
        except ConnectionFailure:
            print("❌ Error: No se pudo conectar a MongoDB Atlas")
            raise
    
    # --- MÉTODOS DE USUARIOS ---
    
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

    # --- MÉTODOS DE PLANTAS ---

    def obtener_plantas(self, filtro_nombre=None):
        """Busca plantas. Si hay filtro, usa regex; si no, trae todas."""
        try:
            if filtro_nombre:
                # La búsqueda "i" es para que no importe mayúsculas/minúsculas
                return list(self.coleccion_plantas.find({
                    "nombre": {"$regex": filtro_nombre, "$options": "i"}
                }))
            return list(self.coleccion_plantas.find())
        except Exception as e:
            print(f"Error al obtener plantas: {e}")
            return []

    def insertar_planta(self, datos_planta):
        """Guarda una nueva planta en la colección."""
        try:
            resultado = self.coleccion_plantas.insert_one(datos_planta)
            return resultado.inserted_id
        except Exception as e:
            print(f"Error al insertar planta: {e}")
            return None
        
    def eliminar_planta(self, planta_id):
        try:
            from bson.objectid import ObjectId
            
            # BORRA EL DOCUMENTO CON EL _id ESPECÍFICO
            
            resultado = self.coleccion_plantas.delete_one({"_id": ObjectId(planta_id)})
            return resultado.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar planta: {e}")
            return False

            # --- MÉTODOS DE FAVORITOS ---

    def alternar_favorito(self, email_usuario, planta_id):
        """Agrega o quita una planta de los favoritos del usuario (Toggle)."""
        try:
            usuario = self.buscar_usuario(email_usuario)
            if not usuario:
                return False

            favoritos = usuario.get('favoritos', [])

            if planta_id in favoritos:
                # Si ya es favorito, lo removemos
                self.usuarios.update_one(
                    {"email": email_usuario},
                    {"$pull": {"favoritos": planta_id}}
                )
            else:
                # Si no es favorito, lo agregamos
                self.usuarios.update_one(
                    {"email": email_usuario},
                    {"$addToSet": {"favoritos": planta_id}}
                )
            return True
        except Exception as e:
            print(f"Error al alternar favorito: {e}")
            return False

    def obtener_favoritos_usuario(self, email_usuario):
        """Devuelve los documentos completos de las plantas favoritas del usuario."""
        try:
            usuario = self.buscar_usuario(email_usuario)
            if not usuario or 'favoritos' not in usuario:
                return []
            
            # Convertimos las IDs de texto a ObjectIds de Mongo para buscarlas
            ids_plantas = [ObjectId(pid) for pid in usuario['favoritos']]
            return list(self.coleccion_plantas.find({"_id": {"$in": ids_plantas}}))
        except Exception as e:
            print(f"Error al obtener favoritos: {e}")
            return []