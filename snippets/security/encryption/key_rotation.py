"""
Key Rotation
Secure key rotation strategies
"""
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, MultiFernet
import secrets


class KeyRotation:
    """Handle cryptographic key rotation"""

    def __init__(self):
        self.keys = []
        self.key_metadata = []
        self._generate_initial_key()

    def _generate_initial_key(self):
        """Generate first key"""
        key = Fernet.generate_key()
        self.keys.append(key)
        self.key_metadata.append({
            'created': datetime.utcnow(),
            'rotated': None,
            'active': True
        })

    def rotate_key(self):
        """Rotate to new key"""
        # Mark old key as rotated
        self.key_metadata[-1]['rotated'] = datetime.utcnow()
        self.key_metadata[-1]['active'] = False
        
        # Generate new key
        new_key = Fernet.generate_key()
        self.keys.append(new_key)
        self.key_metadata.append({
            'created': datetime.utcnow(),
            'rotated': None,
            'active': True
        })

    def get_cipher(self) -> MultiFernet:
        """Get multi-key cipher for decryption"""
        return MultiFernet([Fernet(k) for k in self.keys])

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt with active key"""
        active_cipher = Fernet(self.keys[-1])
        return active_cipher.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt with any valid key"""
        cipher = self.get_cipher()
        return cipher.decrypt(ciphertext)

    def re_encrypt(self, old_ciphertext: bytes) -> bytes:
        """Re-encrypt data with new key"""
        plaintext = self.decrypt(old_ciphertext)
        return self.encrypt(plaintext)

    def should_rotate(self, max_age_days: int = 90) -> bool:
        """Check if key should be rotated"""
        if not self.key_metadata:
            return True
        
        last_key = self.key_metadata[-1]
        age = datetime.utcnow() - last_key['created']
        return age > timedelta(days=max_age_days)


# Example
if __name__ == "__main__":
    kr = KeyRotation()
    
    # Encrypt with first key
    data = b"Sensitive data"
    encrypted = kr.encrypt(data)
    print("✓ Encrypted with key v1")
    
    # Rotate key
    kr.rotate_key()
    print("✓ Rotated to key v2")
    
    # Can still decrypt old data
    decrypted = kr.decrypt(encrypted)
    print(f"✓ Decrypted old data: {decrypted.decode()}")
    
    # Re-encrypt with new key
    re_encrypted = kr.re_encrypt(encrypted)
    print("✓ Re-encrypted with new key")
    
    # Check if rotation needed
    print(f"Should rotate: {kr.should_rotate(max_age_days=90)}")
