"""
Certificate Handling and Validation
Production-ready X.509 certificate utilities
"""
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes
from datetime import datetime


class CertificateHandler:
    """X.509 certificate utilities"""

    @staticmethod
    def load_certificate(filepath: str) -> x509.Certificate:
        """Load certificate from file"""
        with open(filepath, 'rb') as f:
            return x509.load_pem_x509_certificate(f.read())

    @staticmethod
    def get_subject(cert: x509.Certificate) -> dict:
        """Extract subject information"""
        subject = cert.subject
        return {
            'common_name': subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value if subject.get_attributes_for_oid(NameOID.COMMON_NAME) else None,
            'organization': subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value if subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME) else None,
            'country': subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value if subject.get_attributes_for_oid(NameOID.COUNTRY_NAME) else None,
        }

    @staticmethod
    def is_valid(cert: x509.Certificate) -> tuple[bool, str]:
        """Check if certificate is valid"""
        now = datetime.utcnow()
        if now < cert.not_valid_before:
            return False, "Certificate not yet valid"
        if now > cert.not_valid_after:
            return False, "Certificate expired"
        return True, "Certificate valid"

    @staticmethod
    def get_fingerprint(cert: x509.Certificate) -> str:
        """Get certificate fingerprint"""
        return cert.fingerprint(hashes.SHA256()).hex()

    @staticmethod
    def get_san(cert: x509.Certificate) -> list:
        """Get Subject Alternative Names"""
        try:
            san_ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            return [str(name) for name in san_ext.value]
        except x509.ExtensionNotFound:
            return []


# Example
if __name__ == "__main__":
    print("Certificate handling utilities ready")
