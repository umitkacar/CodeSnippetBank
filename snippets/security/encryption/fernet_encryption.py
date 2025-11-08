"""
Fernet Symmetric Encryption
High-level symmetric encryption using Fernet
"""
from cryptography.fernet import Fernet
import base64
import time


class FernetEncryption:
    """Fernet symmetric encryption (AES-128-CBC + HMAC)"""

    @staticmethod
    def generate_key() -> bytes:
        """Generate Fernet key"""
        return Fernet.generate_key()

    def __init__(self, key: bytes = None):
        if key is None:
            key = Fernet.generate_key()
        self.fernet = Fernet(key)
        self.key = key

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data"""
        return self.fernet.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data"""
        return self.fernet.decrypt(ciphertext)

    def encrypt_with_time(self, plaintext: bytes) -> bytes:
        """Encrypt with timestamp"""
        return self.fernet.encrypt_at_time(plaintext, int(time.time()))

    def decrypt_with_ttl(self, ciphertext: bytes, ttl: int) -> bytes:
        """Decrypt with time-to-live check"""
        return self.fernet.decrypt(ciphertext, ttl=ttl)


# Example
if __name__ == "__main__":
    fernet = FernetEncryption()
    plaintext = b"Secret message"
    
    encrypted = fernet.encrypt(plaintext)
    print(f"Encrypted: {encrypted.decode()[:50]}...")
    
    decrypted = fernet.decrypt(encrypted)
    print(f"Decrypted: {decrypted.decode()}")
