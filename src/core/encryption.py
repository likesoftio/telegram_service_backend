import base64
from cryptography.fernet import Fernet
from typing import Optional

from src.core.settings import settings


class EncryptionService:
    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key_str = settings.ENCRYPTION_KEY
            if key_str:
                self.key = base64.urlsafe_b64decode(key_str)
            else:
                self.key = Fernet.generate_key()
        else:
            self.key = key
        
        self.fernet = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypts a string of data"""
        if not data:
            return data
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypts a string of encrypted data"""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            return encrypted_data
    
    def get_key_base64(self) -> str:
        """Returns the encryption key in base64 format"""
        return base64.urlsafe_b64encode(self.key).decode()

encryption_service = EncryptionService()