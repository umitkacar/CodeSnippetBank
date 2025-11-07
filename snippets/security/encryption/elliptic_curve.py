"""
Elliptic Curve Cryptography
ECDH key exchange and ECDSA signatures
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization


class EllipticCurveCrypto:
    """Elliptic curve operations"""

    @staticmethod
    def generate_key() -> ec.EllipticCurvePrivateKey:
        """Generate EC private key"""
        return ec.generate_private_key(ec.SECP256R1())

    @staticmethod
    def ecdh_exchange(private_key: ec.EllipticCurvePrivateKey,
                      peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
        """Perform ECDH key exchange"""
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_key)
        return derived_key

    @staticmethod
    def sign(message: bytes, private_key: ec.EllipticCurvePrivateKey) -> bytes:
        """Sign with ECDSA"""
        return private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    @staticmethod
    def verify(message: bytes, signature: bytes,
               public_key: ec.EllipticCurvePublicKey) -> bool:
        """Verify ECDSA signature"""
        try:
            public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except:
            return False


# Example
if __name__ == "__main__":
    ecc = EllipticCurveCrypto()
    
    # ECDH
    alice_key = ecc.generate_key()
    bob_key = ecc.generate_key()
    
    alice_shared = ecc.ecdh_exchange(alice_key, bob_key.public_key())
    bob_shared = ecc.ecdh_exchange(bob_key, alice_key.public_key())
    
    print(f"✓ ECDH keys match: {alice_shared == bob_shared}")
    
    # ECDSA
    message = b"Message to sign"
    signature = ecc.sign(message, alice_key)
    is_valid = ecc.verify(message, signature, alice_key.public_key())
    print(f"✓ ECDSA signature valid: {is_valid}")
