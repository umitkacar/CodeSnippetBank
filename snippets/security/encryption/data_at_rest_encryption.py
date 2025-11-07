"""
Data at Rest Encryption
Production-ready database field encryption
"""
from cryptography.fernet import Fernet
import base64


class DataAtRestEncryption:
    """Encrypt sensitive database fields"""

    def __init__(self, key: bytes = None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
        self.key = key

    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt database field"""
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt database field"""
        decoded = base64.urlsafe_b64decode(ciphertext.encode())
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode()

    def get_key(self) -> str:
        """Get encryption key"""
        return base64.urlsafe_b64encode(self.key).decode()


# Example
if __name__ == "__main__":
    encryptor = DataAtRestEncryption()
    
    # Encrypt sensitive data
    ssn = "123-45-6789"
    encrypted_ssn = encryptor.encrypt_field(ssn)
    print(f"Encrypted SSN: {encrypted_ssn[:50]}...")
    
    # Decrypt
    decrypted = encryptor.decrypt_field(encrypted_ssn)
    print(f"Decrypted: {decrypted}")
    
    print(f"\nEncryption key: {encryptor.get_key()}")
