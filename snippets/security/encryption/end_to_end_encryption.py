"""
End-to-End Encryption (E2EE)
Production-ready E2EE using hybrid encryption
"""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes
import secrets


class E2EEncryption:
    """End-to-end encryption using hybrid cryptography"""

    @staticmethod
    def generate_keypair() -> tuple:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(65537, 2048)
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def encrypt_message(plaintext: bytes, recipient_public_key: rsa.RSAPublicKey) -> dict:
        """Encrypt message with hybrid encryption"""
        # Generate symmetric key
        symmetric_key = secrets.token_bytes(32)
        iv = secrets.token_bytes(16)

        # Encrypt message with AES
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CTR(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Encrypt symmetric key with RSA
        encrypted_key = recipient_public_key.encrypt(
            symmetric_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return {
            'encrypted_key': encrypted_key,
            'iv': iv,
            'ciphertext': ciphertext
        }

    @staticmethod
    def decrypt_message(encrypted_data: dict, private_key: rsa.RSAPrivateKey) -> bytes:
        """Decrypt message"""
        # Decrypt symmetric key
        symmetric_key = private_key.decrypt(
            encrypted_data['encrypted_key'],
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt message
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CTR(encrypted_data['iv']))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_data['ciphertext']) + decryptor.finalize()

        return plaintext


# Example
if __name__ == "__main__":
    e2e = E2EEncryption()

    # Generate keys for Alice and Bob
    alice_private, alice_public = e2e.generate_keypair()
    bob_private, bob_public = e2e.generate_keypair()

    # Alice sends message to Bob
    message = b"Secret message from Alice to Bob"
    encrypted = e2e.encrypt_message(message, bob_public)
    print("✓ Message encrypted")

    # Bob decrypts message
    decrypted = e2e.decrypt_message(encrypted, bob_private)
    print(f"✓ Decrypted: {decrypted.decode()}")
