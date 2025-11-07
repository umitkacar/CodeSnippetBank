"""
Diffie-Hellman Key Exchange
Secure key exchange protocol
"""
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes


class DiffieHellmanKeyExchange:
    """Diffie-Hellman key exchange"""

    @staticmethod
    def generate_parameters() -> dh.DHParameters:
        """Generate DH parameters (slow, do once)"""
        return dh.generate_parameters(generator=2, key_size=2048)

    @staticmethod
    def generate_private_key(parameters: dh.DHParameters) -> dh.DHPrivateKey:
        """Generate private key"""
        return parameters.generate_private_key()

    @staticmethod
    def derive_shared_secret(
        private_key: dh.DHPrivateKey,
        peer_public_key: dh.DHPublicKey
    ) -> bytes:
        """Derive shared secret"""
        shared_key = private_key.exchange(peer_public_key)
        
        # Derive a fixed-length key from shared secret
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data'
        ).derive(shared_key)
        
        return derived_key


# Example
if __name__ == "__main__":
    dh_kex = DiffieHellmanKeyExchange()
    
    # Generate parameters (shared between parties)
    parameters = dh_kex.generate_parameters()
    print("✓ Generated DH parameters")
    
    # Alice generates key pair
    alice_private = dh_kex.generate_private_key(parameters)
    alice_public = alice_private.public_key()
    
    # Bob generates key pair
    bob_private = dh_kex.generate_private_key(parameters)
    bob_public = bob_private.public_key()
    
    # Both derive same shared secret
    alice_shared = dh_kex.derive_shared_secret(alice_private, bob_public)
    bob_shared = dh_kex.derive_shared_secret(bob_private, alice_public)
    
    print(f"✓ Shared secrets match: {alice_shared == bob_shared}")
    print(f"Shared key: {alice_shared.hex()[:32]}...")
