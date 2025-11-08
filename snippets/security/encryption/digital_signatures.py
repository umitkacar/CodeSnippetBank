"""
Digital Signatures
Production-ready digital signature implementations
"""
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from typing import Union


class DigitalSignatures:
    """Digital signature utilities"""

    @staticmethod
    def sign_rsa(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """Sign with RSA-PSS"""
        return private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    @staticmethod
    def verify_rsa(message: bytes, signature: bytes, public_key: rsa.RSAPublicKey) -> bool:
        """Verify RSA signature"""
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
        except InvalidSignature:
            return False

    @staticmethod
    def generate_ec_key() -> ec.EllipticCurvePrivateKey:
        """Generate ECDSA key"""
        return ec.generate_private_key(ec.SECP256R1())

    @staticmethod
    def sign_ecdsa(message: bytes, private_key: ec.EllipticCurvePrivateKey) -> bytes:
        """Sign with ECDSA"""
        return private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    @staticmethod
    def verify_ecdsa(message: bytes, signature: bytes, public_key: ec.EllipticCurvePublicKey) -> bool:
        """Verify ECDSA signature"""
        try:
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False


# Example
if __name__ == "__main__":
    signer = DigitalSignatures()
    message = b"Document to sign"

    # RSA
    from cryptography.hazmat.primitives.asymmetric import rsa
    rsa_key = rsa.generate_private_key(65537, 2048)
    rsa_sig = signer.sign_rsa(message, rsa_key)
    print(f"RSA signature valid: {signer.verify_rsa(message, rsa_sig, rsa_key.public_key())}")

    # ECDSA
    ec_key = signer.generate_ec_key()
    ec_sig = signer.sign_ecdsa(message, ec_key)
    print(f"ECDSA signature valid: {signer.verify_ecdsa(message, ec_sig, ec_key.public_key())}")
