"""
Cryptographic Hashing Algorithms
Production-ready hashing with multiple algorithms
"""
import hashlib
import hmac
from typing import Optional
import base64


class HashingAlgorithms:
    """Cryptographic hashing utilities"""

    @staticmethod
    def sha256(data: bytes) -> bytes:
        """SHA-256 hash"""
        return hashlib.sha256(data).digest()

    @staticmethod
    def sha512(data: bytes) -> bytes:
        """SHA-512 hash"""
        return hashlib.sha512(data).digest()

    @staticmethod
    def sha3_256(data: bytes) -> bytes:
        """SHA3-256 hash"""
        return hashlib.sha3_256(data).digest()

    @staticmethod
    def blake2b(data: bytes, digest_size: int = 64) -> bytes:
        """BLAKE2b hash"""
        return hashlib.blake2b(data, digest_size=digest_size).digest()

    @staticmethod
    def hmac_sha256(data: bytes, key: bytes) -> bytes:
        """HMAC-SHA256"""
        return hmac.new(key, data, hashlib.sha256).digest()

    @staticmethod
    def verify_hmac(data: bytes, key: bytes, mac: bytes) -> bool:
        """Verify HMAC (constant-time)"""
        expected = hmac.new(key, data, hashlib.sha256).digest()
        return hmac.compare_digest(expected, mac)

    @staticmethod
    def hash_file(filepath: str, algorithm: str = 'sha256') -> str:
        """Hash file contents"""
        hash_obj = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()


# Example usage
if __name__ == "__main__":
    hasher = HashingAlgorithms()
    data = b"Data to hash"

    print(f"SHA-256: {hasher.sha256(data).hex()}")
    print(f"SHA-512: {hasher.sha512(data).hex()[:64]}...")
    print(f"SHA3-256: {hasher.sha3_256(data).hex()}")
    print(f"BLAKE2b: {hasher.blake2b(data).hex()[:64]}...")

    key = b"secret_key"
    mac = hasher.hmac_sha256(data, key)
    print(f"\nHMAC-SHA256: {mac.hex()}")
    print(f"HMAC valid: {hasher.verify_hmac(data, key, mac)}")
