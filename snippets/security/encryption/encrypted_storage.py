"""
Encrypted Storage
Secure key-value storage with encryption
"""
import json
from cryptography.fernet import Fernet
import secrets


class EncryptedStorage:
    """Encrypted key-value storage"""

    def __init__(self, storage_file: str, key: bytes = None):
        self.storage_file = storage_file
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self._data = {}
        self.load()

    def set(self, key: str, value: str):
        """Store encrypted value"""
        encrypted = self.cipher.encrypt(value.encode())
        self._data[key] = encrypted.decode()
        self.save()

    def get(self, key: str) -> str:
        """Retrieve and decrypt value"""
        if key not in self._data:
            return None
        encrypted = self._data[key].encode()
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

    def delete(self, key: str):
        """Delete key"""
        if key in self._data:
            del self._data[key]
            self.save()

    def save(self):
        """Save to file"""
        with open(self.storage_file, 'w') as f:
            json.dump(self._data, f)

    def load(self):
        """Load from file"""
        try:
            with open(self.storage_file, 'r') as f:
                self._data = json.load(f)
        except FileNotFoundError:
            self._data = {}


# Example
if __name__ == "__main__":
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        storage_file = f.name
    
    try:
        storage = EncryptedStorage(storage_file)
        
        storage.set('api_key', 'sk_live_abc123')
        storage.set('password', 'secret_password')
        
        print(f"API Key: {storage.get('api_key')}")
        print(f"Password: {storage.get('password')}")
        print("✓ Encrypted storage working")
    finally:
        os.unlink(storage_file)
