from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os

class GestorTareas:
    def __init__(self):
        # Tu cadena de conexión de Atlas
        uri = "mongodb+srv://luzzz06:UxVkjeZjqCzeNTFE@luzz.jzuseoq.mongodb.net/?appName=luzz"
        
        try:
            # Inicializar el cliente con un timeout para evitar esperas infinitas
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            
            # Seleccionar base de datos y colecciones
            self.db = self.cliente['gestor_tareas'] 
            self.usuarios = self.db['usuarios']
            self.tareas = self.db['tareas'] # Colección adicional común en estos gestores
            
            # Verificación real de conexión (Ping)
            self.cliente.admin.command('ping')
            
            # Configurar índices obligatorios
            self.usuarios.create_index("email", unique=True)
            
            print("✅ Conexión a la Nube Exitosa")
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            # Opcional: podrías lanzar el error para que el programa no siga si falla
            # raise e