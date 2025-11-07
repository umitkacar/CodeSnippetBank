"""API Security Best Practices"""
class APISecurityMiddleware:
    """Comprehensive API security"""
    
    def __init__(self):
        self.rate_limiter = None  # Initialize with rate limiter
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        return api_key.startswith('sk_') and len(api_key) > 32
    
    @staticmethod
    def sanitize_request_params(params: dict) -> dict:
        """Sanitize request parameters"""
        import html
        sanitized = {}
        for key, value in params.items():
            if isinstance(value, str):
                sanitized[key] = html.escape(value)
            else:
                sanitized[key] = value
        return sanitized
    
    @staticmethod
    def get_security_headers() -> dict:
        """Get API security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Strict-Transport-Security': 'max-age=31536000'
        }

if __name__ == "__main__":
    api_sec = APISecurityMiddleware()
    print("✓ API security middleware configured")
