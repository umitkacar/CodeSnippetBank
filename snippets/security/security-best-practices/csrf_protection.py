"""CSRF Protection"""
import secrets
import hmac
import hashlib
from typing import Optional

class CSRFProtection:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token"""
        random_part = secrets.token_urlsafe(32)
        signature = hmac.new(
            self.secret_key,
            f"{session_id}:{random_part}".encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{random_part}.{signature}"
    
    def verify_token(self, token: str, session_id: str) -> bool:
        """Verify CSRF token"""
        try:
            random_part, signature = token.rsplit('.', 1)
            expected_sig = hmac.new(
                self.secret_key,
                f"{session_id}:{random_part}".encode(),
                hashlib.sha256
            ).hexdigest()
            return secrets.compare_digest(signature, expected_sig)
        except:
            return False

if __name__ == "__main__":
    csrf = CSRFProtection("secret_key")
    token = csrf.generate_token("session_123")
    print(f"✓ CSRF token: {token[:30]}...")
    print(f"✓ Valid: {csrf.verify_token(token, 'session_123')}")
