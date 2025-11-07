"""Input Validation - Production-ready validators"""
import re
from typing import Any

class InputValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 255) -> str:
        """Remove dangerous characters"""
        import html
        sanitized = html.escape(input_str[:max_length])
        return sanitized.strip()
    
    @staticmethod
    def validate_url(url: str) -> bool:
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

if __name__ == "__main__":
    validator = InputValidator()
    print(f"Email valid: {validator.validate_email('test@example.com')}")
    print(f"Sanitized: {validator.sanitize_string('<script>alert(1)</script>')}")
