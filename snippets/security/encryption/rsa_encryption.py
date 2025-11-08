"""
RSA Encryption and Digital Signatures
Production-ready RSA asymmetric encryption
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional
import base64


class RSAEncryption:
    """RSA encryption and key management"""

    @staticmethod
    def generate_key_pair(key_size: int = 2048) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def encrypt(plaintext: bytes, public_key: rsa.RSAPublicKey) -> bytes:
        """Encrypt with RSA public key"""
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    @staticmethod
    def decrypt(ciphertext: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """Decrypt with RSA private key"""
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext

    @staticmethod
    def sign(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """Sign message with private key"""
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def verify(message: bytes, signature: bytes, public_key: rsa.RSAPublicKey) -> bool:
        """Verify signature with public key"""
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    @staticmethod
    def save_private_key(private_key: rsa.RSAPrivateKey, filename: str, password: Optional[bytes] = None) -> None:
        """Save private key to file"""
        encryption = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        with open(filename, 'wb') as f:
            f.write(pem)

    @staticmethod
    def save_public_key(public_key: rsa.RSAPublicKey, filename: str) -> None:
        """Save public key to file"""
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(filename, 'wb') as f:
            f.write(pem)

    @staticmethod
    def load_private_key(filename: str, password: Optional[bytes] = None) -> rsa.RSAPrivateKey:
        """Load private key from file"""
        with open(filename, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=password,
                backend=default_backend()
            )
        return private_key  # type: ignore

    @staticmethod
    def load_public_key(filename: str) -> rsa.RSAPublicKey:
        """Load public key from file"""
        with open(filename, 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        return public_key  # type: ignore


# Example usage
if __name__ == "__main__":
    rsa_crypto = RSAEncryption()

    # Generate key pair
    private_key, public_key = rsa_crypto.generate_key_pair(2048)
    print("✓ Generated RSA key pair")

    # Encrypt/Decrypt
    message = b"Secret message for RSA encryption"
    ciphertext = rsa_crypto.encrypt(message, public_key)
    print(f"Encrypted: {base64.b64encode(ciphertext).decode()[:50]}...")

    decrypted = rsa_crypto.decrypt(ciphertext, private_key)
    print(f"Decrypted: {decrypted.decode()}")

    # Sign/Verify
    signature = rsa_crypto.sign(message, private_key)
    print(f"\nSignature: {base64.b64encode(signature).decode()[:50]}...")

    is_valid = rsa_crypto.verify(message, signature, public_key)
    print(f"Signature valid: {is_valid}")
