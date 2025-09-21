import sqlite3
import hashlib
import os
class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            if exc_type is None:
                self.connection.commit()
            self.connection.close()

def hash_password(password: str, salt: str) -> str:
    """Хеширование пароля с солью"""
    return hashlib.sha256((salt + password).encode()).hexdigest()

def generate_salt() -> str:
    """Генерация соли"""
    return os.urandom(16).hex()