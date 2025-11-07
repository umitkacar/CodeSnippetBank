"""
ChaCha20-Poly1305 Encryption
Modern authenticated encryption
"""
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import secrets


class ChaCha20Encryption:
    """ChaCha20-Poly1305 AEAD cipher"""

    def __init__(self, key: bytes = None):
        if key is None:
            key = ChaCha20Poly1305.generate_key()
        self.cipher = ChaCha20Poly1305(key)
        self.key = key

    def encrypt(self, plaintext: bytes, associated_data: bytes = b"") -> tuple[bytes, bytes]:
        """Encrypt with ChaCha20-Poly1305"""
        nonce = secrets.token_bytes(12)
        ciphertext = self.cipher.encrypt(nonce, plaintext, associated_data)
        return nonce, ciphertext

    def decrypt(self, nonce: bytes, ciphertext: bytes,
                associated_data: bytes = b"") -> bytes:
        """Decrypt with ChaCha20-Poly1305"""
        plaintext = self.cipher.decrypt(nonce, ciphertext, associated_data)
        return plaintext


# Example
if __name__ == "__main__":
    chacha = ChaCha20Encryption()
    
    plaintext = b"Message encrypted with ChaCha20"
    aad = b"metadata"
    
    nonce, ciphertext = chacha.encrypt(plaintext, aad)
    print(f"✓ Encrypted with ChaCha20-Poly1305")
    
    decrypted = chacha.decrypt(nonce, ciphertext, aad)
    print(f"✓ Decrypted: {decrypted.decode()}")
