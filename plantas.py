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
            self.comentarios = self.db['comentarios']
            self.sugerencias = self.db['sugerencias']
            
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


    def obtener_plantas(self, filtro_nombre=None):
        """Busca plantas. Si hay filtro, usa regex; si no, trae todas."""
        try:
            if filtro_nombre:
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
            
            resultado = self.coleccion_plantas.delete_one({"_id": ObjectId(planta_id)})
            return resultado.deleted_count > 0
        except Exception as e:
            print(f"Error al eliminar planta: {e}")
            return False

    def alternar_favorito(self, email_usuario, planta_id):
        """Agrega o quita una planta de los favoritos del usuario (Toggle)."""
        try:
            usuario = self.buscar_usuario(email_usuario)
            if not usuario:
                return False

            favoritos = usuario.get('favoritos', [])

            if planta_id in favoritos:
                self.usuarios.update_one(
                    {"email": email_usuario},
                    {"$pull": {"favoritos": planta_id}}
                )
            else:
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
            
            ids_plantas = [ObjectId(pid) for pid in usuario['favoritos']]
            return list(self.coleccion_plantas.find({"_id": {"$in": ids_plantas}}))
        except Exception as e:
            print(f"Error al obtener favoritos: {e}")
            return []
        
    def obtener_planta_por_id(self, planta_id):
        """Busca una sola planta por su ObjectId."""
        try:
            return self.coleccion_plantas.find_one({"_id": ObjectId(planta_id)})
        except Exception as e:
            print(f"Error al obtener planta por ID: {e}")
            return None

    def actualizar_planta(self, planta_id, nuevos_datos):
        """Actualiza los datos de una planta existente."""
        try:
            resultado = self.coleccion_plantas.update_one(
                {"_id": ObjectId(planta_id)},
                {"$set": nuevos_datos}
            )
            return resultado.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar planta: {e}")
            return False

    def obtener_comentarios(self):
        try:
            return list(self.comentarios.find().sort("_id", -1))
        except Exception as e:
            print(f"Error al obtener comentarios: {e}")
            return []

    def insertar_comentario(self, nombre, texto):
        try:
            resultado = self.comentarios.insert_one({
                "nombre": nombre,
                "texto": texto,
                "fecha": datetime.now().strftime("%d/%m/%Y")
            })
            return resultado.inserted_id
        except Exception as e:
            print(f"Error al insertar comentario: {e}")
            return None

    def obtener_todas_sugerencias(self):
        try:
            return list(self.sugerencias.find())
        except Exception as e:
            print(f"Error al obtener sugerencias: {e}")
            return []

    def insertar_sugerencia(self, nombre_planta):
        try:
            resultado = self.sugerencias.insert_one({
                "nombre_planta": nombre_planta,
                "estado": "pendiente"
            })
            return resultado.inserted_id
        except Exception as e:
            print(f"Error al insertar sugerencia: {e}")
            return None

    def actualizar_estado_sugerencia(self, sugerencia_id, nuevo_estado):
        try:
            resultado = self.sugerencias.update_one(
                {"_id": ObjectId(sugerencia_id)},
                {"$set": {"estado": nuevo_estado}}
            )
            return resultado.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar sugerencia: {e}")
            return False
            
    def buscar_sugerencia_por_id(self, sugerencia_id):
        try:
            return self.sugerencias.find_one({"_id": ObjectId(sugerencia_id)})
        except Exception as e:
            print(f"Error al buscar sugerencia: {e}")
            return None
