"""
Authenticated Encryption
Encrypt-then-MAC pattern
"""
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets


class AuthenticatedEncryption:
    """Authenticated encryption using Encrypt-then-MAC"""

    def __init__(self, enc_key: bytes = None, mac_key: bytes = None):
        self.enc_key = enc_key or secrets.token_bytes(32)
        self.mac_key = mac_key or secrets.token_bytes(32)

    def encrypt(self, plaintext: bytes) -> dict:
        """Encrypt and authenticate"""
        # Encrypt
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(self.enc_key), modes.CTR(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        # MAC over IV + ciphertext
        mac = hmac.new(self.mac_key, iv + ciphertext, hashlib.sha256).digest()
        
        return {'iv': iv, 'ciphertext': ciphertext, 'mac': mac}

    def decrypt(self, encrypted_data: dict) -> bytes:
        """Verify and decrypt"""
        iv = encrypted_data['iv']
        ciphertext = encrypted_data['ciphertext']
        mac = encrypted_data['mac']
        
        # Verify MAC
        expected_mac = hmac.new(self.mac_key, iv + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("Authentication failed")
        
        # Decrypt
        cipher = Cipher(algorithms.AES(self.enc_key), modes.CTR(iv))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext


# Example
if __name__ == "__main__":
    ae = AuthenticatedEncryption()
    
    plaintext = b"Authenticated encrypted message"
    encrypted = ae.encrypt(plaintext)
    print("✓ Encrypted with authentication")
    
    decrypted = ae.decrypt(encrypted)
    print(f"✓ Decrypted: {decrypted.decode()}")
    
    # Test tampering
    encrypted['ciphertext'] = b'tampered' + encrypted['ciphertext']
    try:
        ae.decrypt(encrypted)
    except ValueError as e:
        print(f"✓ Tampering detected: {e}")
