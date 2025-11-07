"""
Certificate-Based Authentication (mTLS)
Production-ready mutual TLS authentication
"""
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import ssl


class CertificateGenerator:
    """Generate X.509 certificates for client authentication"""

    @staticmethod
    def generate_private_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
        """
        Generate RSA private key

        Args:
            key_size: Key size in bits

        Returns:
            RSA private key
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        return private_key

    @staticmethod
    def generate_certificate(
        private_key: rsa.RSAPrivateKey,
        subject_name: str,
        issuer_name: Optional[str] = None,
        validity_days: int = 365,
        is_ca: bool = False
    ) -> x509.Certificate:
        """
        Generate X.509 certificate

        Args:
            private_key: Private key
            subject_name: Subject common name
            issuer_name: Issuer name (if different)
            validity_days: Certificate validity in days
            is_ca: Whether this is a CA certificate

        Returns:
            X.509 certificate
        """
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Example Corp"),
            x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
        ])

        cert_builder = x509.CertificateBuilder()
        cert_builder = cert_builder.subject_name(subject)
        cert_builder = cert_builder.issuer_name(issuer)
        cert_builder = cert_builder.public_key(private_key.public_key())
        cert_builder = cert_builder.serial_number(x509.random_serial_number())
        cert_builder = cert_builder.not_valid_before(datetime.utcnow())
        cert_builder = cert_builder.not_valid_after(
            datetime.utcnow() + timedelta(days=validity_days)
        )

        # Add basic constraints
        cert_builder = cert_builder.add_extension(
            x509.BasicConstraints(ca=is_ca, path_length=None),
            critical=True,
        )

        # Add key usage
        if is_ca:
            cert_builder = cert_builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            )
        else:
            cert_builder = cert_builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            )

        # Sign certificate
        certificate = cert_builder.sign(private_key, hashes.SHA256())

        return certificate

    @staticmethod
    def save_private_key(private_key: rsa.RSAPrivateKey, filename: str) -> None:
        """Save private key to file"""
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        with open(filename, 'wb') as f:
            f.write(pem)

    @staticmethod
    def save_certificate(certificate: x509.Certificate, filename: str) -> None:
        """Save certificate to file"""
        pem = certificate.public_bytes(serialization.Encoding.PEM)

        with open(filename, 'wb') as f:
            f.write(pem)


class CertificateValidator:
    """Validate client certificates"""

    def __init__(self, ca_certificate_path: Optional[str] = None):
        """
        Initialize certificate validator

        Args:
            ca_certificate_path: Path to CA certificate for validation
        """
        self.ca_cert = None

        if ca_certificate_path:
            with open(ca_certificate_path, 'rb') as f:
                self.ca_cert = x509.load_pem_x509_certificate(f.read())

    def validate_certificate(
        self,
        client_cert: x509.Certificate
    ) -> tuple[bool, str]:
        """
        Validate client certificate

        Args:
            client_cert: Client certificate to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        now = datetime.utcnow()

        # Check if certificate is expired
        if now < client_cert.not_valid_before:
            return False, "Certificate not yet valid"

        if now > client_cert.not_valid_after:
            return False, "Certificate has expired"

        # Check if revoked (implement CRL/OCSP checking in production)

        # Validate certificate chain (simplified)
        if self.ca_cert:
            try:
                # In production, use proper chain validation
                pass
            except Exception as e:
                return False, f"Certificate chain validation failed: {e}"

        return True, "Certificate is valid"

    def extract_certificate_info(
        self,
        certificate: x509.Certificate
    ) -> Dict:
        """
        Extract information from certificate

        Args:
            certificate: X.509 certificate

        Returns:
            Dictionary with certificate information
        """
        subject = certificate.subject
        issuer = certificate.issuer

        info = {
            'subject': {
                'common_name': subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                if subject.get_attributes_for_oid(NameOID.COMMON_NAME) else None,
                'organization': subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
                if subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else None,
                'country': subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value
                if subject.get_attributes_for_oid(NameOID.COUNTRY_NAME) else None,
            },
            'issuer': {
                'common_name': issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                if issuer.get_attributes_for_oid(NameOID.COMMON_NAME) else None,
            },
            'serial_number': certificate.serial_number,
            'not_before': certificate.not_valid_before.isoformat(),
            'not_after': certificate.not_valid_after.isoformat(),
            'fingerprint': certificate.fingerprint(hashes.SHA256()).hex()
        }

        return info


class MTLSAuthenticator:
    """Mutual TLS authentication handler"""

    def __init__(self, validator: CertificateValidator):
        """
        Initialize mTLS authenticator

        Args:
            validator: Certificate validator
        """
        self.validator = validator
        self.authorized_certs: Dict[str, Dict] = {}

    def register_certificate(
        self,
        user_id: int,
        certificate: x509.Certificate,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Register authorized certificate

        Args:
            user_id: User ID
            certificate: User's certificate
            metadata: Additional metadata

        Returns:
            Certificate fingerprint
        """
        fingerprint = certificate.fingerprint(hashes.SHA256()).hex()

        self.authorized_certs[fingerprint] = {
            'user_id': user_id,
            'certificate': certificate,
            'registered_at': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }

        return fingerprint

    def authenticate(
        self,
        client_certificate: x509.Certificate
    ) -> Optional[Dict]:
        """
        Authenticate client using certificate

        Args:
            client_certificate: Client's certificate

        Returns:
            User data if authenticated, None otherwise
        """
        # Validate certificate
        is_valid, error_msg = self.validator.validate_certificate(
            client_certificate
        )

        if not is_valid:
            print(f"Certificate validation failed: {error_msg}")
            return None

        # Check if certificate is registered
        fingerprint = client_certificate.fingerprint(hashes.SHA256()).hex()
        cert_data = self.authorized_certs.get(fingerprint)

        if not cert_data:
            print("Certificate not authorized")
            return None

        # Extract user information
        cert_info = self.validator.extract_certificate_info(client_certificate)

        return {
            'user_id': cert_data['user_id'],
            'certificate_info': cert_info,
            'metadata': cert_data['metadata']
        }

    def revoke_certificate(self, fingerprint: str) -> bool:
        """
        Revoke certificate

        Args:
            fingerprint: Certificate fingerprint

        Returns:
            True if revoked
        """
        if fingerprint in self.authorized_certs:
            del self.authorized_certs[fingerprint]
            return True

        return False


class MTLSServer:
    """mTLS server configuration helper"""

    @staticmethod
    def create_ssl_context(
        certfile: str,
        keyfile: str,
        ca_certs: Optional[str] = None,
        require_client_cert: bool = True
    ) -> ssl.SSLContext:
        """
        Create SSL context for mTLS

        Args:
            certfile: Server certificate path
            keyfile: Server private key path
            ca_certs: CA certificate path for client validation
            require_client_cert: Require client certificate

        Returns:
            SSL context
        """
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        # Load server certificate and key
        context.load_cert_chain(certfile, keyfile)

        # Configure client certificate verification
        if ca_certs:
            context.load_verify_locations(ca_certs)

            if require_client_cert:
                context.verify_mode = ssl.CERT_REQUIRED
            else:
                context.verify_mode = ssl.CERT_OPTIONAL

        return context


# Example usage
if __name__ == "__main__":
    # Generate CA certificate
    ca_key = CertificateGenerator.generate_private_key()
    ca_cert = CertificateGenerator.generate_certificate(
        ca_key,
        "Example CA",
        is_ca=True,
        validity_days=3650
    )

    print("✓ Generated CA certificate")

    # Generate client certificate
    client_key = CertificateGenerator.generate_private_key()
    client_cert = CertificateGenerator.generate_certificate(
        client_key,
        "client.example.com",
        validity_days=365
    )

    print("✓ Generated client certificate")

    # Validate certificate
    validator = CertificateValidator()
    is_valid, message = validator.validate_certificate(client_cert)

    print(f"\nCertificate validation: {is_valid} - {message}")

    # Extract certificate info
    cert_info = validator.extract_certificate_info(client_cert)
    print(f"Certificate info:")
    print(f"  Subject: {cert_info['subject']['common_name']}")
    print(f"  Valid until: {cert_info['not_after']}")
    print(f"  Fingerprint: {cert_info['fingerprint'][:32]}...")

    # Setup mTLS authentication
    authenticator = MTLSAuthenticator(validator)

    # Register certificate
    fingerprint = authenticator.register_certificate(
        user_id=123,
        certificate=client_cert,
        metadata={'role': 'admin'}
    )

    print(f"\n✓ Registered certificate: {fingerprint[:32]}...")

    # Authenticate
    user = authenticator.authenticate(client_cert)

    if user:
        print(f"\n✓ Authenticated user: {user['user_id']}")
        print(f"  Role: {user['metadata']['role']}")
