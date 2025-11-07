"""
Streaming Encryption
Production-ready encryption for large files/streams
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets


class StreamingEncryption:
    """Encrypt/decrypt large files in chunks"""

    def __init__(self, key: bytes = None):
        self.key = key or secrets.token_bytes(32)

    def encrypt_stream(self, input_file: str, output_file: str, chunk_size: int = 64*1024):
        """Encrypt file in streaming fashion"""
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CTR(iv))
        encryptor = cipher.encryptor()

        with open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                # Write IV first
                f_out.write(iv)
                
                # Encrypt in chunks
                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break
                    encrypted_chunk = encryptor.update(chunk)
                    f_out.write(encrypted_chunk)
                
                # Finalize
                f_out.write(encryptor.finalize())

    def decrypt_stream(self, input_file: str, output_file: str, chunk_size: int = 64*1024):
        """Decrypt file in streaming fashion"""
        with open(input_file, 'rb') as f_in:
            # Read IV
            iv = f_in.read(16)
            
            cipher = Cipher(algorithms.AES(self.key), modes.CTR(iv))
            decryptor = cipher.decryptor()

            with open(output_file, 'wb') as f_out:
                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break
                    decrypted_chunk = decryptor.update(chunk)
                    f_out.write(decrypted_chunk)
                
                f_out.write(decryptor.finalize())


# Example
if __name__ == "__main__":
    stream_enc = StreamingEncryption()
    print("✓ Streaming encryption ready for large files")
