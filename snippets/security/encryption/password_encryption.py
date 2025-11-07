"""
Password-Based Encryption
Encrypt data with user password using PBKDF2
"""
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64
import secrets


class PasswordBasedEncryption:
    """Encrypt data using password"""

    @staticmethod
    def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """Derive encryption key from password"""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    @staticmethod
    def encrypt(plaintext: bytes, password: str) -> dict:
        """Encrypt data with password"""
        key, salt = PasswordBasedEncryption.derive_key(password)
        cipher = Fernet(key)
        ciphertext = cipher.encrypt(plaintext)
        
        return {
            'salt': base64.b64encode(salt).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode()
        }

    @staticmethod
    def decrypt(encrypted_data: dict, password: str) -> bytes:
        """Decrypt data with password"""
        salt = base64.b64decode(encrypted_data['salt'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        
        key, _ = PasswordBasedEncryption.derive_key(password, salt)
        cipher = Fernet(key)
        plaintext = cipher.decrypt(ciphertext)
        
        return plaintext


# Example
if __name__ == "__main__":
    pbe = PasswordBasedEncryption()
    
    plaintext = b"Secret data protected by password"
    password = "MySecurePassword123!"
    
    encrypted = pbe.encrypt(plaintext, password)
    print(f"✓ Encrypted with password")
    
    decrypted = pbe.decrypt(encrypted, password)
    print(f"✓ Decrypted: {decrypted.decode()}")
