"""
Envelope Encryption
Multi-layer encryption for cloud security
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets


class EnvelopeEncryption:
    """Envelope encryption (encrypt data key with master key)"""

    def __init__(self, master_key: bytes):
        """Initialize with master key (KMS key)"""
        self.master_key = master_key

    def encrypt(self, plaintext: bytes) -> dict:
        """Encrypt data using envelope encryption"""
        # Generate data encryption key (DEK)
        dek = secrets.token_bytes(32)
        dek_iv = secrets.token_bytes(16)
        
        # Encrypt plaintext with DEK
        cipher = Cipher(algorithms.AES(dek), modes.CTR(dek_iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # Encrypt DEK with master key
        master_iv = secrets.token_bytes(16)
        master_cipher = Cipher(algorithms.AES(self.master_key), modes.CTR(master_iv))
        master_encryptor = master_cipher.encryptor()
        encrypted_dek = master_encryptor.update(dek) + master_encryptor.finalize()
        
        return {
            'ciphertext': ciphertext,
            'dek_iv': dek_iv,
            'encrypted_dek': encrypted_dek,
            'master_iv': master_iv
        }

    def decrypt(self, envelope: dict) -> bytes:
        """Decrypt data using envelope encryption"""
        # Decrypt DEK with master key
        master_cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.CTR(envelope['master_iv'])
        )
        master_decryptor = master_cipher.decryptor()
        dek = master_decryptor.update(envelope['encrypted_dek']) + master_decryptor.finalize()
        
        # Decrypt plaintext with DEK
        cipher = Cipher(algorithms.AES(dek), modes.CTR(envelope['dek_iv']))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(envelope['ciphertext']) + decryptor.finalize()
        
        return plaintext


# Example
if __name__ == "__main__":
    # Master key from KMS
    master_key = secrets.token_bytes(32)
    
    envelope = EnvelopeEncryption(master_key)
    
    plaintext = b"Data protected by envelope encryption"
    encrypted = envelope.encrypt(plaintext)
    print("✓ Encrypted with envelope encryption")
    
    decrypted = envelope.decrypt(encrypted)
    print(f"✓ Decrypted: {decrypted.decode()}")
