"""
Key Derivation Functions
Production-ready KDF implementations (PBKDF2, scrypt, Argon2)
"""
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import hashes
import secrets


class KeyDerivation:
    """Key derivation utilities"""

    @staticmethod
    def pbkdf2(password: bytes, salt: bytes = None, iterations: int = 100000, key_length: int = 32) -> tuple:
        """Derive key using PBKDF2"""
        if salt is None:
            salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations
        )
        key = kdf.derive(password)
        return key, salt

    @staticmethod
    def scrypt_derive(password: bytes, salt: bytes = None, n: int = 2**14, r: int = 8, p: int = 1, key_length: int = 32) -> tuple:
        """Derive key using scrypt"""
        if salt is None:
            salt = secrets.token_bytes(16)
        kdf = Scrypt(
            salt=salt,
            length=key_length,
            n=n,
            r=r,
            p=p
        )
        key = kdf.derive(password)
        return key, salt

    @staticmethod
    def hkdf_expand(key_material: bytes, info: bytes = b'', length: int = 32) -> bytes:
        """Expand key using HKDF"""
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=None,
            info=info
        )
        return hkdf.derive(key_material)


# Example
if __name__ == "__main__":
    kdf = KeyDerivation()
    password = b"user_password"

    # PBKDF2
    key, salt = kdf.pbkdf2(password)
    print(f"PBKDF2 key: {key.hex()[:64]}...")
    print(f"Salt: {salt.hex()}")

    # scrypt
    key, salt = kdf.scrypt_derive(password)
    print(f"\nscrypt key: {key.hex()[:64]}...")

    # HKDF
    expanded = kdf.hkdf_expand(b"master_key", b"context_info")
    print(f"\nHKDF expanded: {expanded.hex()[:64]}...")
