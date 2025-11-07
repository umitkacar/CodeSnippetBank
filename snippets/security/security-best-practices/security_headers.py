"""Security Headers"""
from typing import Dict

class SecurityHeaders:
    @staticmethod
    def get_secure_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }

if __name__ == "__main__":
    headers = SecurityHeaders.get_secure_headers()
    for name, value in headers.items():
        print(f"{name}: {value}")
