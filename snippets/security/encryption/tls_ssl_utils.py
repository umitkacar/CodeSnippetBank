"""
TLS/SSL Utilities
Production-ready TLS/SSL helpers
"""
import ssl
import socket
from typing import Optional, Dict
from datetime import datetime


class TLSUtils:
    """TLS/SSL utility functions"""

    @staticmethod
    def create_secure_context(
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        ca_certs: Optional[str] = None,
        min_version: int = ssl.TLSVersion.TLSv1_2
    ) -> ssl.SSLContext:
        """Create secure SSL context"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH if certfile else ssl.Purpose.SERVER_AUTH)

        # Set minimum TLS version
        context.minimum_version = min_version

        # Load certificates
        if certfile and keyfile:
            context.load_cert_chain(certfile, keyfile)

        if ca_certs:
            context.load_verify_locations(ca_certs)

        # Security settings
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        return context

    @staticmethod
    def get_certificate_info(hostname: str, port: int = 443) -> Dict:
        """Get SSL certificate information"""
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return {
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'version': cert['version'],
                    'serial_number': cert['serialNumber'],
                    'not_before': cert['notBefore'],
                    'not_after': cert['notAfter'],
                    'sans': cert.get('subjectAltName', [])
                }

    @staticmethod
    def verify_certificate(hostname: str, port: int = 443) -> tuple[bool, str]:
        """Verify SSL certificate"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    # Check expiration
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    if datetime.now() > not_after:
                        return False, "Certificate expired"
                    return True, "Certificate valid"
        except ssl.SSLError as e:
            return False, f"SSL error: {e}"
        except Exception as e:
            return False, f"Error: {e}"


# Example
if __name__ == "__main__":
    tls = TLSUtils()
    # Create context
    context = tls.create_secure_context()
    print(f"✓ Created secure TLS context (min version: {context.minimum_version})")
