"""
AES Encryption (Advanced Encryption Standard)
Production-ready AES encryption with multiple modes
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as sym_padding
import secrets
import base64
from typing import Tuple


class AESEncryption:
    """AES encryption handler with multiple modes"""

    def __init__(self, key_size: int = 256):
        """
        Initialize AES encryption

        Args:
            key_size: Key size in bits (128, 192, or 256)
        """
        if key_size not in [128, 192, 256]:
            raise ValueError("Key size must be 128, 192, or 256 bits")

        self.key_size = key_size
        self.key_bytes = key_size // 8

    def generate_key(self) -> bytes:
        """
        Generate random AES key

        Returns:
            Random key bytes
        """
        return secrets.token_bytes(self.key_bytes)

    def encrypt_gcm(
        self,
        plaintext: bytes,
        key: bytes,
        associated_data: bytes = b""
    ) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt using AES-GCM (recommended mode)

        Args:
            plaintext: Data to encrypt
            key: Encryption key
            associated_data: Additional authenticated data

        Returns:
            Tuple of (iv, ciphertext, tag)
        """
        # Generate random IV (12 bytes for GCM)
        iv = secrets.token_bytes(12)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()

        # Add associated data
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Get authentication tag
        tag = encryptor.tag

        return iv, ciphertext, tag

    def decrypt_gcm(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
        tag: bytes,
        associated_data: bytes = b""
    ) -> bytes:
        """
        Decrypt using AES-GCM

        Args:
            ciphertext: Encrypted data
            key: Decryption key
            iv: Initialization vector
            tag: Authentication tag
            associated_data: Additional authenticated data

        Returns:
            Decrypted plaintext

        Raises:
            InvalidTag: If authentication fails
        """
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # Add associated data
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    def encrypt_cbc(
        self,
        plaintext: bytes,
        key: bytes
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt using AES-CBC with PKCS7 padding

        Args:
            plaintext: Data to encrypt
            key: Encryption key

        Returns:
            Tuple of (iv, ciphertext)
        """
        # Generate random IV (16 bytes for CBC)
        iv = secrets.token_bytes(16)

        # Pad plaintext
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()

        # Encrypt
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return iv, ciphertext

    def decrypt_cbc(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes
    ) -> bytes:
        """
        Decrypt using AES-CBC

        Args:
            ciphertext: Encrypted data
            key: Decryption key
            iv: Initialization vector

        Returns:
            Decrypted plaintext
        """
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # Decrypt
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad
        unpadder = sym_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext

    def encrypt_ctr(
        self,
        plaintext: bytes,
        key: bytes
    ) -> Tuple[bytes, bytes]:
        """
        Encrypt using AES-CTR (Counter mode)

        Args:
            plaintext: Data to encrypt
            key: Encryption key

        Returns:
            Tuple of (nonce, ciphertext)
        """
        # Generate random nonce (16 bytes)
        nonce = secrets.token_bytes(16)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CTR(nonce),
            backend=default_backend()
        )

        encryptor = cipher.encryptor()

        # Encrypt (no padding needed for CTR)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return nonce, ciphertext

    def decrypt_ctr(
        self,
        ciphertext: bytes,
        key: bytes,
        nonce: bytes
    ) -> bytes:
        """
        Decrypt using AES-CTR

        Args:
            ciphertext: Encrypted data
            key: Decryption key
            nonce: Nonce

        Returns:
            Decrypted plaintext
        """
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CTR(nonce),
            backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext


class AESFileEncryption:
    """File encryption using AES-GCM"""

    def __init__(self, key: bytes):
        """
        Initialize file encryption

        Args:
            key: 256-bit encryption key
        """
        self.aes = AESEncryption(256)
        self.key = key

    def encrypt_file(
        self,
        input_path: str,
        output_path: str,
        chunk_size: int = 64 * 1024
    ) -> None:
        """
        Encrypt file using AES-GCM

        Args:
            input_path: Path to input file
            output_path: Path to output file
            chunk_size: Chunk size for streaming
        """
        with open(input_path, 'rb') as f_in:
            plaintext = f_in.read()

        # Encrypt
        iv, ciphertext, tag = self.aes.encrypt_gcm(plaintext, self.key)

        # Write encrypted file
        with open(output_path, 'wb') as f_out:
            # Write header: IV length (1 byte) + IV + tag
            f_out.write(len(iv).to_bytes(1, 'big'))
            f_out.write(iv)
            f_out.write(tag)
            f_out.write(ciphertext)

    def decrypt_file(
        self,
        input_path: str,
        output_path: str
    ) -> None:
        """
        Decrypt file using AES-GCM

        Args:
            input_path: Path to encrypted file
            output_path: Path to output file
        """
        with open(input_path, 'rb') as f_in:
            # Read header
            iv_length = int.from_bytes(f_in.read(1), 'big')
            iv = f_in.read(iv_length)
            tag = f_in.read(16)
            ciphertext = f_in.read()

        # Decrypt
        plaintext = self.aes.decrypt_gcm(ciphertext, self.key, iv, tag)

        # Write decrypted file
        with open(output_path, 'wb') as f_out:
            f_out.write(plaintext)


# Example usage
if __name__ == "__main__":
    aes = AESEncryption(256)

    # Generate key
    key = aes.generate_key()
    print(f"Generated key: {base64.b64encode(key).decode()}")

    # Test AES-GCM (recommended)
    print("\n=== AES-GCM ===")
    plaintext = b"Secret message for AES-GCM encryption"
    associated_data = b"user_id=123"

    iv, ciphertext, tag = aes.encrypt_gcm(plaintext, key, associated_data)
    print(f"IV: {base64.b64encode(iv).decode()}")
    print(f"Ciphertext: {base64.b64encode(ciphertext).decode()}")
    print(f"Tag: {base64.b64encode(tag).decode()}")

    decrypted = aes.decrypt_gcm(ciphertext, key, iv, tag, associated_data)
    print(f"Decrypted: {decrypted.decode()}")

    # Test AES-CBC
    print("\n=== AES-CBC ===")
    plaintext = b"Secret message for AES-CBC encryption"

    iv, ciphertext = aes.encrypt_cbc(plaintext, key)
    print(f"IV: {base64.b64encode(iv).decode()}")
    print(f"Ciphertext: {base64.b64encode(ciphertext).decode()}")

    decrypted = aes.decrypt_cbc(ciphertext, key, iv)
    print(f"Decrypted: {decrypted.decode()}")

    # Test AES-CTR
    print("\n=== AES-CTR ===")
    plaintext = b"Secret message for AES-CTR encryption"

    nonce, ciphertext = aes.encrypt_ctr(plaintext, key)
    print(f"Nonce: {base64.b64encode(nonce).decode()}")
    print(f"Ciphertext: {base64.b64encode(ciphertext).decode()}")

    decrypted = aes.decrypt_ctr(ciphertext, key, nonce)
    print(f"Decrypted: {decrypted.decode()}")
