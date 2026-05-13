from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import os

class GestorTareas:
    def __init__(self):
        uri = "mongodb+srv://luzzz06:UxVkjeZjqCzeNTFE@luzz.jzuseoq.mongodb.net/?appName=luzz"
        
        try:
            self.cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
            
            self.db = self.cliente['gestor_tareas'] 
            self.usuarios = self.db['usuarios']
            self.tareas = self.db['tareas']
            
            self.cliente.admin.command('ping')
            
            self.usuarios.create_index("email", unique=True)
            
            print("✅ Conexión a la Nube Exitosa")
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
