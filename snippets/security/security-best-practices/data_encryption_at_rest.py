"""Data Encryption at Rest"""
from cryptography.fernet import Fernet

class DataEncryptionAtRest:
    """Encrypt sensitive data before storage"""
    
    def __init__(self, encryption_key: bytes = None):
        if encryption_key is None:
            encryption_key = Fernet.generate_key()
        self.cipher = Fernet(encryption_key)
        self.key = encryption_key
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a database field"""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt a database field"""
        return self.cipher.decrypt(ciphertext.encode()).decode()
    
    @staticmethod
    def fields_to_encrypt() -> list:
        """List of fields that should be encrypted"""
        return [
            'ssn',
            'credit_card_number',
            'bank_account',
            'api_keys',
            'oauth_tokens',
            'password_reset_tokens'
        ]

if __name__ == "__main__":
    encryptor = DataEncryptionAtRest()
    encrypted = encryptor.encrypt_field('123-45-6789')
    print(f"✓ Encrypted SSN: {encrypted[:30]}...")
    print(f"✓ Decrypted: {encryptor.decrypt_field(encrypted)}")
