"""Secure Logging Practices"""
import logging
import re

class SecureLogger:
    """Logger that doesn't log sensitive data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Patterns to redact
        self.sensitive_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
            (r'\b\d{16}\b', '[CARD]'),  # Credit card
            (r'password["\']?\s*[:=]\s*["\']?(\w+)', r'password=****'),
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?(\w+)', r'api_key=****'),
        ]
    
    def sanitize_log_message(self, message: str) -> str:
        """Remove sensitive data from log message"""
        sanitized = message
        for pattern, replacement in self.sensitive_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized
    
    def safe_log(self, level: str, message: str):
        """Log with sanitization"""
        sanitized = self.sanitize_log_message(message)
        getattr(self.logger, level)(sanitized)

if __name__ == "__main__":
    logger = SecureLogger()
    logger.safe_log('info', 'User login: password=mysecretpass')
    print("✓ Sensitive data redacted in logs")
