from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime
import os

class Plantas:
    def __init__(self):
        # 1. Tu URI con las credenciales que verificamos
        uri = "mongodb+srv://luzzz06:UxVkjeZjqCzeNTFE@luzz.jzuseoq.mongodb.net/?appName=luzz"
        try:
            # 2. Conexión al cliente
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            
            # 3. Acceso a la base de datos y colecciones
            self.db = self.cliente['gestor_tareas']
            self.usuarios = self.db['usuarios']
            self.tareas = self.db['tareas']
            
            # 4. El "Ping" para confirmar que entramos
            self.cliente.admin.command('ping')
            
            # 5. Crear índice único para el email
            self.usuarios.create_index("email", unique=True)
            
            print("✅ Conexión a la Nube Exitosa")
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

# --- PRUEBA DE CONEXIÓN ---
if __name__ == "__main__":
    gestor = GestorTareas()